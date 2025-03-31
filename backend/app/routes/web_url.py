from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
import random
import string

from app.models import WebURL
from app.schemas import WebURLCreate, WebURLRead, WebURLResponse
from app.database import get_db

router = APIRouter()

def make_suffix(length=7):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

async def get_url_by_suffix(suffix: str, db: AsyncSession):
    return (await db.execute(
        select(WebURL).where(WebURL.suffix == suffix)
    )).scalars().first()


@router.post("/shorten", response_model=WebURLResponse)
async def create_short_url(web_url: WebURLCreate, request: Request, db: AsyncSession = Depends(get_db)):
    if web_url.custom_suffix:
        existing_url = await get_url_by_suffix(web_url.custom_suffix, db)
        if existing_url:
            if existing_url.expires_at < datetime.now():
                await db.delete(existing_url)
                await db.commit()
            else:
                raise HTTPException(status_code=400, detail="Custom suffix is already in use")
        suffix = web_url.custom_suffix
    else:
        suffix = make_suffix()
        existing_url = await get_url_by_suffix(suffix, db)
        while existing_url:
            if existing_url.expires_at < datetime.now():
                await db.delete(existing_url)
                await db.commit()
            else:
                suffix = make_suffix()
            existing_url = await get_url_by_suffix(suffix, db)
    
    # DB 
    db_url = WebURL(
        original_url=str(web_url.original_url),
        suffix=suffix
    )
    db.add(db_url)
    await db.commit()
    await db.refresh(db_url)
    
    # Make the short URL
    base_url = str(request.base_url)
    short_url = f"{base_url}r/{suffix}"
    
    return {
        "short_url": short_url,
        "original_url": db_url.original_url,
        "expires_at": db_url.expires_at
    }


@router.get("/r/{suffix}")
async def redirect_to_url(suffix: str, db: AsyncSession = Depends(get_db)):
    db_url = await get_url_by_suffix(suffix, db)
    
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    if db_url.expires_at < datetime.now():
        raise HTTPException(status_code=410, detail="Short URL has expired, please create a new one")

    db_url.clicks += 1
    await db.commit()
    
    return RedirectResponse(url=db_url.original_url, status_code=307)


@router.get("/info/{suffix}", response_model=WebURLRead)
async def get_url_information(suffix: str, db: AsyncSession = Depends(get_db)):
    db_url = await get_url_by_suffix(suffix, db)
    
    if not db_url:
        raise HTTPException(status_code=404, detail="Short URL not found")
    
    return db_url