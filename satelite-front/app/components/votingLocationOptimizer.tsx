'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { X, Plus, Minus, CheckCircle2, XCircle, Search, RotateCcw } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Progress } from '@/components/ui/progress'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Card, CardContent } from '@/components/ui/card'
import axios from 'axios'
import Image from "next/image";

// 型定義
interface Location {
  lng: string
  lat: string
  city_name: string
  city_code: string
  population: string
  population_density: string
  wsf_density: string
  space: string
  voter_turnout: string
  location_score: string
  reviews: string
  user_rating: string
  display_name: string
  display_address: string
  station: string
  name: string
  good_point: string
  bad_point: string
}

// 定数
const MAP_CENTER = { lat: 35.6895, lng: 139.6917 } // 地図の中心座標（東京）
const MAX_POPULATION = 1000000 // 最大人口
const MAX_POPULATION_DENSITY = 30000 // 最大人口密度（人/km²）
const MAX_SPACE = 10000 // 最大面積（m²）
const WALKING_SPEED = 80 // 歩行速度（メートル/分）
const MAX_SYMBOL_SIZE = 60 // シンボルの最大サイズ
const MIN_SYMBOL_SIZE = 5  // シンボルの最小サイズ
const GOOGLE_MAPS_API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY
const GOOGLE_MAPS_API_URL = `https://maps.googleapis.com/maps/api/js?key=${GOOGLE_MAPS_API_KEY}&callback=initMap&language=ja`

// ヘルパー関数
const calculateProgressValue = (value: number, max: number) => (Math.min(value, max) / max) * 100

const formatDistance = (distanceM: number) => {
  const distanceKm = Math.round(distanceM / 100) / 10
  return `${distanceKm}km`
}

const calculateWalkingTime = (distanceM: number) => Math.round(distanceM / WALKING_SPEED)

const calculateSymbolSize = (score: number) => {
  const normalizedScore = Math.min(Math.max(score, 0), 100) / 100
  return MIN_SYMBOL_SIZE + Math.pow(normalizedScore, 2) * (MAX_SYMBOL_SIZE - MIN_SYMBOL_SIZE)
}

const getColorForScore = (score: number) => {
  const colors = [
    '#00ff00', // 緑（最低スコア）
    '#40ff00',
    '#80ff00',
    '#bfff00',
    '#ffff00', // 黄（中間スコア）
    '#ffbf00',
    '#ff8000',
    '#ff4000',
    '#ff0000'  // 赤（最高スコア）
  ]
  const index = Math.floor(score / 100 * 8)
  return colors[Math.min(index, 8)]
}


// メインコンポーネント
export default function VotingLocationOptimizer() {
  // State
  const [symbols, setSymbols] = useState<google.maps.Marker[]>([])
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null)
  const [locations, setLocations] = useState<Location[]>([])
  const [searchCriteria, setSearchCriteria] = useState('')
  const [isSearchResult, setIsSearchResult] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  // Refs
  const mapRef = useRef<google.maps.Map | null>(null)
  const mapContainerRef = useRef<HTMLDivElement>(null)

  // Callbacks
  const handleLocationSelect = useCallback((location: Location) => {
    setSelectedLocation(location)
    if (mapRef.current) {
      mapRef.current.panTo({ lat: parseFloat(location.lat), lng: parseFloat(location.lng) })
      mapRef.current.setZoom(15) // オプション：ズームレベルを調整
    }
  }, [])

  const handleSearchCriteriaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setSearchCriteria(e.target.value)
  }

  const handleSearch = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get(`https://q7ady2awyhhpkjrxxyrueqeqki0ljxxq.lambda-url.ap-northeast-1.on.aws/`, {
        params: { input_text: searchCriteria, count: 10 }
      });
      console.log(searchCriteria);
      setLocations(response.data.Items);
      setIsSearchResult(true);
    } catch (error) {
      console.error('Error searching locations:', error);
      setLocations([]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSearch = () => {
    // 候補地一覧を削除
    handleDeleteAllLocations()
    
    // 候補地一覧を再取得
    handleFetchAllLocations()
    
    setIsSearchResult(false)
  }

  const handleFetchAllLocations = async () => {
    setIsLoading(true)
    try {
      await fetchLocations()
    } finally {
      setIsLoading(false)
    }
  }

  const handleDeleteAllLocations = () => {
    setLocations([])
    symbols.forEach(symbol => symbol.setMap(null))
    setSymbols([])
  }

  // 地図の初期化
  const initializeMap = useCallback(() => {
    if (typeof window.google === 'undefined' || !mapContainerRef.current) {
      console.error('Google Maps API is not loaded or map container is not available')
      return
    }

    mapRef.current = new window.google.maps.Map(mapContainerRef.current, {
      center: MAP_CENTER,
      zoom: 13,
      disableDefaultUI: false,
      zoomControl: true,
      mapTypeControl: true,
      scaleControl: true,
      streetViewControl: true,
      rotateControl: true,
      fullscreenControl: true
    })
  }, [])

  // シンボルの作成
  const createSymbols = useCallback((locations: Location[]) => {
    if (!mapRef.current) return []

    return locations.map(location => {
      const score = parseFloat(location.location_score)
      const symbol = new google.maps.Marker({
        position: { lat: parseFloat(location.lat), lng: parseFloat(location.lng) },
        map: mapRef.current,
        icon: {
          path: google.maps.SymbolPath.CIRCLE,
          scale: calculateSymbolSize(score),
          fillColor: getColorForScore(score),
          fillOpacity: 0.7,
          strokeWeight: 2,
          strokeColor: "#FFFFFF",
        },
        title: `${location.name} (Score: ${location.location_score})`,
      })

      symbol.addListener('click', () => handleLocationSelect(location))

      return symbol
    })
  }, [handleLocationSelect])

  // 候補地全件取得APIの呼び出し
  const fetchLocations = async () => {
    try {
      const response = await axios.get('https://z57gxouzr5upsvh7q24hbrw5vq0exqhj.lambda-url.ap-northeast-1.on.aws/locations')
      setLocations(response.data)
    } catch (err) {
      console.error('Error fetching locations:', err)
      setLocations([])
    }
  }

  // Effects
  useEffect(() => {
    fetchLocations()
  }, [])

  // シンボルの作成
  useEffect(() => {
    if (mapRef.current && locations.length > 0) {
      // 既存のシンボルを削除
      symbols.forEach(symbol => symbol.setMap(null))

      const newSymbols = createSymbols(locations)
      setSymbols(newSymbols)

      // 新しいシンボルをマップに追加
      newSymbols.forEach(symbol => symbol.setMap(mapRef.current))
    }
  }, [locations, createSymbols])

  // Google Maps APIの読み込み
  useEffect(() => {
    if (typeof window !== 'undefined' && !window.google) {
      const script = document.createElement('script')
      script.src = GOOGLE_MAPS_API_URL
      script.async = true
      script.defer = true
      document.head.appendChild(script)
    } else if (window.google) {
      initializeMap()
    }
  }, [initializeMap])

  useEffect(() => {
    window.initMap = initializeMap
  }, [initializeMap])

  // Render functions
  // 位置詳細の表示
  const renderLocationDetails = () => {
    if (!selectedLocation) return null

    const stationInfo = JSON.parse(selectedLocation.station)
    const walkingMinutes = calculateWalkingTime(stationInfo.distanceM)

    return (
      <div className="w-96 bg-white border-l">
        <div className="p-6">
          <div className="flex items-start justify-between mb-8">
            <div className="flex-grow">
              <h2 className="text-xl font-medium text-gray-800 mb-2">{selectedLocation.display_name}</h2>
              <div className="flex items-center space-x-2 mb-3">
                <span className="text-2xl font-bold" style={{ color: getColorForScore(parseFloat(selectedLocation.location_score)) }}>
                  score: {parseFloat(selectedLocation.location_score).toFixed(1)}
                </span>
              </div>
              <Progress 
                value={parseFloat(selectedLocation.location_score)} 
                max={100}
                className="h-3 bg-blue-100" 
              />
              <div className="mt-4 space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2 flex items-center">
                    <CheckCircle2 className="w-4 h-4 mr-2 text-green-500" />
                    Pros
                  </h4>
                  <p className="text-sm text-gray-800 ml-6">
                    {selectedLocation.good_point || "No pros available"}
                  </p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-2 flex items-center">
                    <XCircle className="w-4 h-4 mr-2 text-red-500" />
                    Cons
                  </h4>
                  <p className="text-sm text-gray-800 ml-6">
                    {selectedLocation.bad_point || "No cons available"}
                  </p>
                </div>
              </div>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setSelectedLocation(null)}
              className="text-gray-500 hover:text-gray-700"
            >
              <X className="h-4 w-4" />
            </Button>
          </div>

          <div className="space-y-8">
            <div>
              <h3 className="font-medium mb-4 text-gray-700 border-b pb-2">施設情報</h3>
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-1">住所</h4>
                  <p className="text-sm text-gray-800">{selectedLocation.display_address}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-1">緯度経度</h4>
                  <p className="text-sm text-gray-800">緯度: {selectedLocation.lat}</p>
                  <p className="text-sm text-gray-800">経度: {selectedLocation.lng}</p>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-600 mb-1">最寄り駅</h4>
                  <p className="text-sm text-gray-800">
                    {stationInfo.station} ({stationInfo.companyDisplayLabel} {stationInfo.rail}) - 
                    徒歩約{walkingMinutes}分 ({formatDistance(stationInfo.distanceM)})
                  </p>
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">面積</span>
                    <span className="text-gray-800">{parseFloat(selectedLocation.space).toFixed(1)}m²</span>
                  </div>
                  <Progress 
                    value={calculateProgressValue(parseFloat(selectedLocation.space), MAX_SPACE)}
                    max={100}
                    className="h-2 bg-gray-200" 
                  />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">建物密度</span>
                    <span className="text-gray-800">{parseFloat(selectedLocation.wsf_density).toFixed(2)}</span>
                  </div>
                  <Progress 
                    value={calculateProgressValue(parseFloat(selectedLocation.wsf_density), 1)}
                    max={100}
                    className="h-2 bg-gray-200" 
                  />
                </div>
              </div>
            </div>

            <div>
              <h3 className="font-medium mb-4 text-gray-700 border-b pb-2">地域情報</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">人口</span>
                    <span className="text-gray-800">{parseFloat(selectedLocation.population).toFixed(1)}人</span>
                  </div>
                  <Progress 
                    value={calculateProgressValue(parseFloat(selectedLocation.population), MAX_POPULATION)}
                    max={100}
                    className="h-2 bg-gray-200" 
                  />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">人口密度</span>
                    <span className="text-gray-800">{parseFloat(selectedLocation.population_density).toFixed(1)}人/km²</span>
                  </div>
                  <Progress 
                    value={calculateProgressValue(parseFloat(selectedLocation.population_density), MAX_POPULATION_DENSITY)}
                    max={100}
                    className="h-2 bg-gray-200" 
                  />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-gray-600">投票率</span>
                    <span className="text-gray-800">{parseFloat(selectedLocation.voter_turnout).toFixed(1)}%</span>
                  </div>
                  <Progress 
                    value={parseFloat(selectedLocation.voter_turnout)}
                    max={100}
                    className="h-2 bg-gray-200" 
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // 左サイドバーの表示
  const renderLeftSidebar = () => (
    <div className="w-64 p-4 border-r bg-white overflow-y-auto h-screen">
      <div className="space-y-6">
        <div>
          <div className="flex items-center space-x-2">
            <Image
              className="dark:invert"
              src="/logo.png"
              alt="Next.js logo"
              width={50}
              height={50}
              priority
            />
            <h2 className="text-lg font-semibold">GeoVote</h2>
          </div>
        </div>

        <div className="space-y-4">
          <div>
            <Label htmlFor="searchCriteria">投票所の特徴</Label>
            <Textarea
              id="searchCriteria"
              name="searchCriteria"
              value={searchCriteria}
              onChange={handleSearchCriteriaChange}
              placeholder="求める投票所の特徴を自由に入力してください（例：広い駐車場がある、バリアフリー設備が整っている、など）"
              className="h-32"
            />
          </div>
          <div className="flex flex-col space-y-2">
            <Button onClick={handleSearch} className="w-full" disabled={isLoading}>
              {isLoading ? (
                <>
                  <span className="animate-spin mr-2">⏳</span>
                  検索中...
                </>
              ) : (
                <>
                  <Search className="w-4 h-4 mr-2" />
                  検索
                </>
              )}
            </Button>
            {isSearchResult && (
              <Button onClick={handleResetSearch} variant="outline" className="w-full">
                <RotateCcw className="w-4 h-4 mr-2" />
                リセット
              </Button>
            )}
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-md font-semibold">候補地一覧</h3>
          {locations.sort((a, b) => parseFloat(b.location_score) - parseFloat(a.location_score)).map((location) => (
            <Card key={location.display_name} className="cursor-pointer" onClick={() => handleLocationSelect(location)}>
              <CardContent className="p-4">
                <h4 className="font-semibold mb-1">{location.display_name}</h4>
                <p className="text-sm text-gray-600 mb-1">{location.display_address}</p>
                <p className="text-sm font-bold">スコア: {parseFloat(location.location_score).toFixed(1)}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )

  // メインマップエリアの表示
  const renderMainMapArea = () => (
    <div className="flex-1 relative">
      <div ref={mapContainerRef} className="w-full h-full" style={{ minHeight: '400px' }} />
      <div className="absolute bottom-4 right-4 space-y-2">
        <Button variant="secondary" size="icon" className="bg-white">
          <Plus className="h-4 w-4" />
        </Button>
        <Button variant="secondary" size="icon" className="bg-white">
          <Minus className="h-4 w-4" />
        </Button>
      </div>
    </div>
  )

  return (
    <div className="flex h-screen overflow-hidden">
      {renderLeftSidebar()}
      {renderMainMapArea()}
      {renderLocationDetails()}
    </div>
  )
}

// グローバル型定義
declare global {
  interface Window {
    google: typeof google
    initMap: () => void
  }
}