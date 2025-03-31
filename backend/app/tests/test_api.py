import pytest
from app.models import WebURL
from datetime import datetime, timedelta
from sqlalchemy.future import select

# TEST POST /shorten
@pytest.mark.asyncio
async def test_create_short_url_successfully(client, test_url):
    test_obj = {"original_url": test_url}
    response = await client.post("/shorten", json=test_obj)
    assert response.status_code == 200
    data = response.json()
    assert "short_url" in data
    assert data["original_url"] == test_url
    assert "expires_at" in data

@pytest.mark.asyncio
async def test_create_custom_short_url_successfully(client, test_url):
    test_obj = {"original_url": test_url, "custom_suffix": "Mario"}
    response = await client.post("/shorten", json=test_obj)
    assert response.status_code == 200
    data = response.json()
    assert data["short_url"] == "http://test/r/Mario"
    assert data["original_url"] == test_url
    assert "expires_at" in data

@pytest.mark.asyncio
async def test_create_custom_short_url_repeated(client, db_session, test_url, create_url):
    test_obj = {"original_url": test_url, "custom_suffix": "Mario"}
    response = await client.post("/shorten", json=test_obj)
    assert response.status_code == 400
    assert response.json()["detail"] == "Custom suffix is already in use"


# TEST GET /r/{suffix}
@pytest.mark.asyncio
async def test_redirect_to_url_successfully(client, db_session, test_url, create_url):
    response = await client.get("/r/Mario", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["Location"] == test_url

@pytest.mark.asyncio
async def test_redirect_to_url_not_found(client, db_session, test_url):
    response = await client.get("/r/notused", follow_redirects=False)
    assert response.status_code == 404
    assert response.json()["detail"] == "Short URL not found"

@pytest.mark.asyncio
async def test_redirect_to_url_expired(client, db_session, test_url):
    expired_url = WebURL(
        original_url=test_url,
        suffix="expired",
        created_at=datetime.now(),
        expires_at=datetime.now() - timedelta(days=1),
    )
    db_session.add(expired_url)
    await db_session.commit()

    response = await client.get("/r/expired", follow_redirects=False)
    assert response.status_code == 410
    assert response.json()["detail"] == "Short URL has expired, please create a new one"


# TEST GET /info/{suffix}
@pytest.mark.asyncio
async def test_get_url_info_successfully(client, db_session, test_url, create_url):
    response = await client.get("/info/Mario")
    assert response.status_code == 200
    data = response.json()
    assert data["original_url"] == test_url
    assert data["suffix"] == "Mario"
    assert data["clicks"] == 0
    assert "expires_at" in data


# TEST Clicks Count
@pytest.mark.asyncio
async def test_clicked_count_db(client, db_session, test_url, create_url):
    # Get url with suffix 'Mario' in DB
    db_url = (await db_session.execute(
        select(WebURL).where(WebURL.suffix == 'Mario')
    )).scalars().first()
    previous_clicks = db_url.clicks

    response = await client.get("/r/Mario")
    assert response.status_code == 307
    
    # Check if the clicks count increased in DB
    await db_session.refresh(db_url)
    assert db_url.clicks == previous_clicks + 1

