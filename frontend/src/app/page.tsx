"use client"

import { useState } from 'react'
import { isValidUrl } from '@/utils/validations'

export default function Home() {
  const [url, setUrl] = useState('')
  const [suffix, setSuffix] = useState('')
  const [shortUrl, setShortUrl] = useState('')
  const [infoSuffix, setInfoSuffix] = useState('')
  const [timesClicked, setTimesClicked] = useState('')
  const [error, setError] = useState('')
  const [error2, setError2] = useState('')
  const [copied, setCopied] = useState(false)
  const [loading, setLoading] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError('')
    setShortUrl('')
    
    if (!isValidUrl(url)) {
      setError('Please enter a valid URL')
      return
    }
    
    setLoading(true)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/shorten`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          original_url: url,
          custom_suffix: suffix
        }),
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to shorten URL')
      }
      
      setShortUrl(data.short_url)
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  async function handleClickedCountSubmit(e: React.FormEvent) {
    e.preventDefault()
    setError2('')
    setTimesClicked('')
    
    setLoading(true)
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/info/${infoSuffix}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'Failed to retrieve URL information')
      }
      
      setTimesClicked(data.clicks)
      if (data.clicks === 0) {
        setTimesClicked("00")
      }
    } catch (error) {
      setError2(error instanceof Error ? error.message : 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  async function copyToClipboard() {
    navigator.clipboard.writeText(shortUrl)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }
  
  return (
    <main className="min-h-screen bg-rose-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-xl shadow-lg p-6 space-y-6">
        <div className="text-center">
          <h1 className="text-3xl font-bold text-rose-600 mb-2">URL Shortener</h1>
          <p className="text-gray-600">
            Shorten a URL and track click statistics
          </p>
          <p className="text-gray-500 text-sm">
            (They expire after 3 days)
          </p>
        </div>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-3">
            <div>
              <div className="space-y-2">
                <label htmlFor="url" className="sr-only">URL to shorten</label>
                <input
                  id="url"
                  name="url"
                  type="text"
                  required
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent"
                  placeholder="Enter a URL to shorten"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                />
                <label htmlFor="suffix" className="sr-only">Custom suffix</label>
                <input
                  id="suffix"
                  name="suffix"
                  type="text"
                  className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent"
                  placeholder="Enter a custom suffix (optional)"
                  value={suffix}
                  onChange={(e) => setSuffix(e.target.value)}
                />
              </div>
            </div>
          </div>

          {error && <p className="text-red-500 text-sm">{error}</p>}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-rose-500 hover:bg-rose-600 text-white font-medium py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Shortening...' : 'Shorten URL'}
            </button>
          </div>
        </form>

        {shortUrl && (
          <div className="bg-rose-50 rounded-lg p-4 space-y-3">
            <h2 className="text-lg font-medium text-gray-700">Your shortened URL</h2>
            <div className="flex items-center justify-between bg-white rounded-lg p-2">
              <h3 className="text-sm font-mono text-rose-600 truncate">{shortUrl}</h3>
              <button
                onClick={copyToClipboard}
                className="bg-rose-100 hover:bg-rose-200 text-rose-600 text-sm font-medium py-1 px-3 rounded transition duration-200"
              >
                {copied ? 'Copied!' : 'Copy'}
              </button>
            </div>
          </div>
        )}

        <form onSubmit={handleClickedCountSubmit} className="space-y-4">
          <div className="space-y-3">
            <div>
              <label htmlFor="infoSuffix" className="sr-only">URL to see info of</label>
              <input
                id="infoSuffix"
                name="infoSuffix"
                type="text"
                required
                className="w-full px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-rose-400 focus:border-transparent"
                placeholder="Enter a suffix to see URL Clicks"
                value={infoSuffix}
                onChange={(e) => setInfoSuffix(e.target.value)}
              />
            </div>
          </div>

          {error2 && <p className="text-red-500 text-sm">{error2}</p>}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-rose-500 hover:bg-rose-600 text-white font-medium py-2 px-4 rounded-lg transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Searching...' : 'Times Clicked'}
            </button>
          </div>
        </form>

        {timesClicked && (
          <div className="bg-rose-50 rounded-lg p-4 text-center">
            <h2 className="text-gray-700">This shortened URL has been clicked <span className="font-bold text-rose-600">{timesClicked}</span> times</h2>
          </div>
        )}
      </div>
    </main>
  );
}