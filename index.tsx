import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  TextInput,
  Modal,
  Alert,
  Dimensions,
  FlatList,
  ActivityIndicator,
  Platform,
  RefreshControl,
  KeyboardAvoidingView,
  Keyboard,
  TouchableWithoutFeedback,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { WebView } from 'react-native-webview';
import axios from 'axios';

const { width, height } = Dimensions.get('window');
const API_URL = process.env.EXPO_PUBLIC_BACKEND_URL || 'http://localhost:8001';

const api = axios.create({
  baseURL: `${API_URL}/api`,
  timeout: 10000,
});

// Theme definitions
const themes = {
  dark: {
    background: '#000000',
    surface: '#1A1A1A',
    surfaceLight: '#2A2A2A',
    surfaceDark: '#0A0A0A',
    text: '#FFFFFF',
    textSecondary: '#888888',
    textMuted: '#666666',
    border: '#333333',
    accent: '#4A90E2',
    success: '#4CAF50',
    danger: '#F44336',
    warning: '#FF9800',
    card: '#1A1A1A',
    input: '#333333',
    modalOverlay: 'rgba(0,0,0,0.8)',
    tabBar: '#0A0A0A',
    mapPanel: '#111111',
  },
  light: {
    background: '#F5F5F5',
    surface: '#FFFFFF',
    surfaceLight: '#FAFAFA',
    surfaceDark: '#E8E8E8',
    text: '#1A1A1A',
    textSecondary: '#666666',
    textMuted: '#999999',
    border: '#E0E0E0',
    accent: '#4A90E2',
    success: '#4CAF50',
    danger: '#F44336',
    warning: '#FF9800',
    card: '#FFFFFF',
    input: '#F0F0F0',
    modalOverlay: 'rgba(0,0,0,0.5)',
    tabBar: '#FFFFFF',
    mapPanel: '#FFFFFF',
  },
};

// Types
interface GameState {
  id: string;
  balance: number;
  home_airport: string;
  current_date: string;
  total_revenue: number;
  total_expenses: number;
  flights_completed: number;
  tutorial_seen?: boolean;
  theme?: string;
  difficulty?: string;
  certifications?: Record<string, boolean>;
  certification_in_progress?: string;
}

interface Certification {
  id: string;
  name: string;
  form: string;
  cost: number;
  time_seconds: number;
  description: string;
  prerequisites: string[];
  unlocks: string;
  completed: boolean;
  available: boolean;
  in_progress: boolean;
  training_remaining: number;
}

interface Aircraft {
  id: string;
  brand: string;
  model: string;
  type: string;
  capacity: number;
  cargo_capacity: number;
  fuel_capacity: number;
  fuel_burn: number;
  range: number;
  cruise_speed: number;
  price: number;
}

interface OwnedAircraft {
  id: string;
  aircraft_id: string;
  name: string;
  current_airport: string;
  status: string;
  details: Aircraft;
}

interface Airport {
  iata: string;
  name: string;
  city: string;
  country: string;
  lat: number;
  lon: number;
  congestion: number;
}

interface Route {
  id: string;
  aircraft_id: string;
  origin: string;
  destination: string;
  distance: number;
  flight_type: string;
  status: string;
  progress: number;
  revenue: number;
  costs: number;
  flight_duration: number;
  passengers: number;
  cargo_weight: number;
  ticket_price?: number;
  cargo_rate?: number;
  current_position?: { lat: number; lon: number };
  origin_coords?: { lat: number; lon: number };
  destination_coords?: { lat: number; lon: number };
  aircraft_name?: string;
  aircraft_details?: Aircraft;
  heading?: number;
}

interface Loan {
  id: string;
  amount: number;
  remaining: number;
  interest_rate: number;
  monthly_payment: number;
  term_months: number;
  months_paid: number;
}

interface Weather {
  airport_iata: string;
  condition: string;
  wind_speed: number;
  visibility: number;
  temperature: number;
  delay_hours: number;
  extra_cost_percent: number;
}

const TABS = [
  { id: 'home', icon: 'home', label: 'Home' },
  { id: 'map', icon: 'globe', label: 'Map' },
  { id: 'aircraft', icon: 'airplane', label: 'Fleet' },
  { id: 'routes', icon: 'navigate', label: 'Routes' },
  { id: 'weather', icon: 'cloud', label: 'Weather' },
  { id: 'finances', icon: 'wallet', label: 'Finance' },
  { id: 'settings', icon: 'settings', label: 'Settings' },
];

export default function AirlineSimulator() {
  const [activeTab, setActiveTab] = useState('home');
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [ownedAircraft, setOwnedAircraft] = useState<OwnedAircraft[]>([]);
  const [airports, setAirports] = useState<Airport[]>([]);
  const [activeRoutes, setActiveRoutes] = useState<Route[]>([]);
  const [allRoutes, setAllRoutes] = useState<Route[]>([]);
  const [loans, setLoans] = useState<Loan[]>([]);
  const [aircraftDatabase, setAircraftDatabase] = useState<Record<string, Aircraft[]>>({});
  const [badWeather, setBadWeather] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [scheduling, setScheduling] = useState(false);
  const [keyboardVisible, setKeyboardVisible] = useState(false);
  const [theme, setTheme] = useState<'dark' | 'light'>('dark');
  
  // Get current theme colors
  const colors = themes[theme];
  
  // Difficulty selection states
  const [showDifficultySelect, setShowDifficultySelect] = useState(false);
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('');
  const [selectedHomeAirport, setSelectedHomeAirport] = useState<Airport | null>(null);
  const [difficultyAirportSearch, setDifficultyAirportSearch] = useState('');
  const [startingGame, setStartingGame] = useState(false);
  
  // Certifications (for hard mode)
  const [certifications, setCertifications] = useState<Certification[]>([]);
  const [startingCert, setStartingCert] = useState<string | null>(null);
  
  // Modal states
  const [showTutorial, setShowTutorial] = useState(false);
  const [showHomeAirportModal, setShowHomeAirportModal] = useState(false);
  const [showAircraftModal, setShowAircraftModal] = useState(false);
  const [showRouteModal, setShowRouteModal] = useState(false);
  const [showLoanModal, setShowLoanModal] = useState(false);
  const [showLoanPaymentModal, setShowLoanPaymentModal] = useState(false);
  const [showSellModal, setShowSellModal] = useState(false);
  
  // Form states
  const [selectedBrand, setSelectedBrand] = useState<string>('');
  const [selectedAircraft, setSelectedAircraft] = useState<Aircraft | null>(null);
  const [aircraftName, setAircraftName] = useState('');
  const [useLoan, setUseLoan] = useState(false);
  const [loanAmount, setLoanAmount] = useState('');
  const [loanTerm, setLoanTerm] = useState('60');
  const [airportSearch, setAirportSearch] = useState('');
  
  // Route form states
  const [selectedPlane, setSelectedPlane] = useState<OwnedAircraft | null>(null);
  const [selectedOrigin, setSelectedOrigin] = useState<Airport | null>(null);
  const [selectedDestination, setSelectedDestination] = useState<Airport | null>(null);
  const [flightType, setFlightType] = useState<'passenger' | 'cargo'>('passenger');
  const [flightMode, setFlightMode] = useState<'charter' | 'scheduled'>('charter');
  const [ticketPrice, setTicketPrice] = useState('');
  const [cargoRate, setCargoRate] = useState('');
  const [estimatedProfit, setEstimatedProfit] = useState<any>(null);
  const [destinationWeather, setDestinationWeather] = useState<Weather | null>(null);
  
  // Loan payment
  const [selectedLoan, setSelectedLoan] = useState<Loan | null>(null);
  const [paymentAmount, setPaymentAmount] = useState('');
  
  // Sell aircraft
  const [aircraftToSell, setAircraftToSell] = useState<OwnedAircraft | null>(null);
  
  // Map state - prevent resets
  const [mapInitialized, setMapInitialized] = useState(false);
  const webviewRef = useRef<WebView | null>(null);
  const iframeRef = useRef<HTMLIFrameElement | null>(null);

  // Generate map HTML only ONCE using useMemo - this is the critical fix
  const staticMapHtml = useMemo(() => {
    return `<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <style>
    body{margin:0;padding:0;-webkit-tap-highlight-color:transparent;}
    #map{width:100%;height:100vh;touch-action:manipulation;}
    .airport-marker{cursor:pointer !important;pointer-events:auto !important;}
    .leaflet-interactive{cursor:pointer !important;pointer-events:auto !important;}
    .leaflet-container{cursor:crosshair;}
    .leaflet-marker-icon,.leaflet-marker-shadow{display:block !important;}
    .pulse-ring{animation:pulse 1s ease-out;animation-iteration-count:1;}
    @keyframes pulse{0%{transform:scale(1);opacity:1;}100%{transform:scale(2.5);opacity:0;}}
  </style>
</head>
<body>
  <div id="map"></div>
  <script>
    var map = L.map('map', {zoomControl: true, tap: true, tapTolerance: 30}).setView([20, 0], 2);
    var airportMarkers = {};
    var airportData = {};
    var routeLines = [];
    var planeMarkers = [];
    var rangeCircle = null;
    var previewLine = null;
    var clickTimeout = null;
    
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OSM'
    }).addTo(map);
    
    function sendToParent(data) {
      try {
        var msg = JSON.stringify(data);
        console.log('Sending to parent:', msg);
        if (window.ReactNativeWebView) {
          window.ReactNativeWebView.postMessage(msg);
        } else if (window.parent && window.parent !== window) {
          window.parent.postMessage(data, '*');
        }
      } catch(e) {
        console.error('Send error:', e);
      }
    }
    
    function showTapFeedback(lat, lon) {
      var feedbackCircle = L.circleMarker([lat, lon], {
        radius: 20,
        fillColor: '#4A90E2',
        color: '#4A90E2',
        weight: 2,
        fillOpacity: 0.3,
        className: 'pulse-ring',
        interactive: false
      }).addTo(map);
      setTimeout(function() { map.removeLayer(feedbackCircle); }, 500);
    }
    
    function handleAirportTap(iata, lat, lon) {
      if (clickTimeout) clearTimeout(clickTimeout);
      clickTimeout = setTimeout(function() {
        console.log('Airport tapped:', iata);
        showTapFeedback(lat, lon);
        sendToParent({type: 'airport_click', iata: iata});
      }, 50);
    }
    
    function updateAirports(airports) {
      Object.values(airportMarkers).forEach(function(m) { 
        map.removeLayer(m); 
      });
      airportMarkers = {};
      airportData = {};
      
      airports.forEach(function(a) {
        airportData[a.iata] = {lat: a.lat, lon: a.lon, city: a.city};
        
        var color = a.isOrigin ? '#4CAF50' : a.isDestination ? '#F44336' : a.isHome ? '#4A90E2' : '#888888';
        // Smaller markers - still clickable but less visual clutter
        var radius = (a.isOrigin || a.isDestination) ? 10 : 6;
        
        var marker = L.circleMarker([a.lat, a.lon], {
          radius: radius,
          fillColor: color,
          color: '#ffffff',
          weight: 2,
          fillOpacity: 0.85,
          bubblingMouseEvents: false
        }).addTo(map);
        
        // Direct click handler - no event delegation
        marker.on('click', function(e) {
          L.DomEvent.stopPropagation(e);
          L.DomEvent.preventDefault(e);
          handleAirportTap(a.iata, a.lat, a.lon);
        });
        
        // Also handle touch events directly for mobile
        marker.on('touchend', function(e) {
          L.DomEvent.stopPropagation(e);
          L.DomEvent.preventDefault(e);
          handleAirportTap(a.iata, a.lat, a.lon);
        });
        
        marker.bindTooltip('<b>' + a.iata + '</b> - ' + a.city, {
          direction: 'top',
          offset: [0, -12],
          permanent: false
        });
        
        // Bring marker to front on hover
        marker.on('mouseover', function() { marker.bringToFront(); });
        
        airportMarkers[a.iata] = marker;
      });
    }
    
    // Store active route data for continuous animation
    var activeRouteData = {};
    var animationInterval = null;
    
    function startContinuousAnimation() {
      if (animationInterval) return;
      
      animationInterval = setInterval(function() {
        var now = Date.now();
        
        planeMarkers.forEach(function(marker) {
          var routeId = marker._routeId;
          var data = activeRouteData[routeId];
          if (!data) return;
          
          // Calculate time elapsed since last update (in hours, game time)
          var elapsedMs = now - data.lastUpdate;
          // New: 1 real second = 10 game minutes = 0.167 hours
          var elapsedGameHours = (elapsedMs / 1000) * 0.167;
          
          // Calculate distance traveled (km)
          var speedKmH = data.speed || 200; // Default cruise speed
          var distanceTraveled = speedKmH * elapsedGameHours;
          
          // Calculate new position along the route
          var totalDistance = data.totalDistance || 1000;
          var progressIncrement = distanceTraveled / totalDistance;
          data.currentProgress = Math.min(1, (data.currentProgress || data.progress) + progressIncrement);
          
          // Interpolate position
          var newLat = data.origin.lat + (data.dest.lat - data.origin.lat) * data.currentProgress;
          var newLon = data.origin.lon + (data.dest.lon - data.origin.lon) * data.currentProgress;
          
          marker.setLatLng([newLat, newLon]);
          marker.setTooltipContent('<b>' + (data.name || 'Aircraft') + '</b><br>' + Math.round(data.currentProgress * 100) + '%');
          
          data.lastUpdate = now;
        });
      }, 100); // Update every 100ms for smooth movement
    }
    
    function updateRoutes(routes) {
      // Keep track of existing plane markers
      var existingPlanes = {};
      planeMarkers.forEach(function(m) {
        if (m._routeId) existingPlanes[m._routeId] = m;
      });
      
      // Remove old route lines
      routeLines.forEach(function(l) { map.removeLayer(l); });
      routeLines = [];
      var newPlaneMarkers = [];
      var newRouteData = {};
      
      routes.forEach(function(r) {
        if (r.origin && r.dest) {
          var line = L.polyline([
            [r.origin.lat, r.origin.lon],
            [r.dest.lat, r.dest.lon]
          ], {color: '#4A90E2', weight: 2, dashArray: '5, 10', interactive: false}).addTo(map);
          routeLines.push(line);
          
          if (r.pos) {
            var routeId = r.name || 'route-' + r.origin.lat + r.dest.lat;
            var existingMarker = existingPlanes[routeId];
            
            // Store route data for continuous animation
            newRouteData[routeId] = {
              origin: r.origin,
              dest: r.dest,
              progress: r.progress,
              currentProgress: activeRouteData[routeId] ? activeRouteData[routeId].currentProgress : r.progress,
              heading: r.heading,
              name: r.name,
              speed: r.speed || 250,
              totalDistance: r.distance || 1000,
              lastUpdate: Date.now()
            };
            
            if (existingMarker) {
              // Update existing marker
              var icon = L.divIcon({
                className: 'plane-icon',
                html: '<div style="font-size:24px;transform:rotate(' + (r.heading - 45) + 'deg);transition:transform 0.3s;">✈️</div>',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
              });
              existingMarker.setIcon(icon);
              
              // Sync progress from server
              newRouteData[routeId].currentProgress = r.progress;
              existingMarker.setLatLng([r.pos.lat, r.pos.lon]);
              
              newPlaneMarkers.push(existingMarker);
              delete existingPlanes[routeId];
            } else {
              // Create new marker
              var icon = L.divIcon({
                className: 'plane-icon',
                html: '<div style="font-size:24px;transform:rotate(' + (r.heading - 45) + 'deg);">✈️</div>',
                iconSize: [28, 28],
                iconAnchor: [14, 14]
              });
              var planeMarker = L.marker([r.pos.lat, r.pos.lon], {icon: icon}).addTo(map);
              planeMarker._routeId = routeId;
              planeMarker.bindTooltip('<b>' + (r.name || 'Aircraft') + '</b><br>' + Math.round(r.progress * 100) + '%');
              newPlaneMarkers.push(planeMarker);
            }
          }
        }
      });
      
      // Remove markers for routes that no longer exist
      Object.values(existingPlanes).forEach(function(m) {
        map.removeLayer(m);
      });
      
      planeMarkers = newPlaneMarkers;
      activeRouteData = newRouteData;
      
      // Start continuous animation if there are planes
      if (planeMarkers.length > 0) {
        startContinuousAnimation();
      }
    }
    
    function updateRange(range) {
      if (rangeCircle) {
        map.removeLayer(rangeCircle);
        rangeCircle = null;
      }
      if (range && range.lat && range.lon && range.range) {
        rangeCircle = L.circle([range.lat, range.lon], {
          radius: range.range * 1000,
          fillColor: '#4A90E2',
          fillOpacity: 0.1,
          color: '#4A90E2',
          weight: 2,
          dashArray: '5, 5',
          interactive: false
        }).addTo(map);
      }
    }
    
    function updatePreview(preview) {
      if (previewLine) {
        map.removeLayer(previewLine);
        previewLine = null;
      }
      if (preview && preview.origin && preview.dest) {
        previewLine = L.polyline([
          [preview.origin.lat, preview.origin.lon],
          [preview.dest.lat, preview.dest.lon]
        ], {color: '#FF9800', weight: 3, interactive: false}).addTo(map);
      }
    }
    
    window.addEventListener('message', function(e) {
      var data = e.data;
      if (!data || !data.type) return;
      
      if (data.type === 'fullUpdate') {
        if (data.airports) updateAirports(data.airports);
        if (data.routes !== undefined) updateRoutes(data.routes || []);
        updateRange(data.range);
        updatePreview(data.preview);
      }
    });
    
    setTimeout(function() { sendToParent({type: 'mapReady'}); }, 500);
  </script>
</body>
</html>`;
  }, []);

  // Send updates to map without regenerating it
  const sendMapUpdate = useCallback(() => {
    const airportsData = airports.map(a => ({
      iata: a.iata,
      lat: a.lat,
      lon: a.lon,
      city: a.city,
      isHome: a.iata === gameState?.home_airport,
      isOrigin: selectedOrigin?.iata === a.iata,
      isDestination: selectedDestination?.iata === a.iata,
    }));
    
    const routesData = activeRoutes.map(r => ({
      origin: r.origin_coords,
      dest: r.destination_coords,
      pos: r.current_position,
      heading: r.heading || 0,
      name: r.aircraft_name,
      progress: r.progress,
      speed: r.aircraft_details?.cruise_speed || 250,
      distance: r.distance || 1000,
    }));
    
    const rangeData = selectedPlane && selectedOrigin ? {
      lat: selectedOrigin.lat,
      lon: selectedOrigin.lon,
      range: selectedPlane.details?.range || 1000
    } : null;
    
    const previewData = selectedOrigin && selectedDestination ? {
      origin: { lat: selectedOrigin.lat, lon: selectedOrigin.lon },
      dest: { lat: selectedDestination.lat, lon: selectedDestination.lon }
    } : null;
    
    const updateMessage = {
      type: 'fullUpdate',
      airports: airportsData,
      routes: routesData,
      range: rangeData,
      preview: previewData
    };
    
    // Send to iframe (web)
    if (Platform.OS === 'web' && iframeRef.current?.contentWindow) {
      iframeRef.current.contentWindow.postMessage(updateMessage, '*');
    }
    
    // Send to WebView (native)
    if (Platform.OS !== 'web' && webviewRef.current) {
      webviewRef.current.injectJavaScript(`
        window.postMessage(${JSON.stringify(updateMessage)}, '*');
        true;
      `);
    }
  }, [airports, activeRoutes, selectedPlane, selectedOrigin, selectedDestination, gameState?.home_airport]);

  // Handle airport click from map
  const handleAirportClick = useCallback((iata: string) => {
    console.log('handleAirportClick called with:', iata, 'selectedPlane:', selectedPlane?.name);
    const airport = airports.find(a => a.iata === iata);
    if (!airport) {
      console.log('Airport not found:', iata);
      return;
    }
    
    // If no plane selected, alert user
    if (!selectedPlane) {
      Alert.alert('Select Aircraft First', 'Please select an aircraft from the list below before choosing a destination.');
      return;
    }
    
    // Don't allow selecting origin as destination
    if (airport.iata === selectedOrigin?.iata) {
      Alert.alert('Invalid Selection', 'This is your origin airport. Please select a different destination.');
      return;
    }
    
    // Set destination
    console.log('Setting destination to:', airport.iata);
    setSelectedDestination(airport);
  }, [airports, selectedPlane, selectedOrigin]);

  // Listen for messages from iframe (web only)
  useEffect(() => {
    if (Platform.OS !== 'web') return;
    
    const handleMessage = (e: MessageEvent) => {
      const data = e.data;
      console.log('Received message from iframe:', data);
      if (!data || typeof data !== 'object') return;
      
      if (data.type === 'mapReady') {
        console.log('Map is ready!');
        setMapInitialized(true);
        // Small delay to ensure map is fully loaded
        setTimeout(() => sendMapUpdate(), 100);
      }
      
      if (data.type === 'airport_click' && data.iata) {
        console.log('Airport click received:', data.iata);
        handleAirportClick(data.iata);
      }
    };
    
    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [sendMapUpdate, handleAirportClick]);

  // Update map when relevant data changes (but don't regenerate HTML)
  useEffect(() => {
    if (mapInitialized) {
      sendMapUpdate();
    }
  }, [mapInitialized, selectedPlane, selectedOrigin, selectedDestination, activeRoutes, airports, sendMapUpdate]);

  // Keyboard listeners
  useEffect(() => {
    const showSub = Keyboard.addListener('keyboardDidShow', () => setKeyboardVisible(true));
    const hideSub = Keyboard.addListener('keyboardDidHide', () => setKeyboardVisible(false));
    return () => { showSub.remove(); hideSub.remove(); };
  }, []);

  const fetchData = useCallback(async () => {
    try {
      const [gameRes, ownedRes, airportsRes, aircraftRes, routesRes, activeRoutesRes, loansRes, weatherRes] = await Promise.all([
        api.get('/game'),
        api.get('/aircraft/owned'),
        api.get('/airports'),
        api.get('/aircraft'),
        api.get('/routes'),
        api.get('/routes/active'),
        api.get('/loans'),
        api.get('/weather/alerts/bad'),
      ]);
      
      setGameState(gameRes.data);
      setOwnedAircraft(ownedRes.data);
      setAirports(airportsRes.data);
      setAircraftDatabase(aircraftRes.data);
      setAllRoutes(routesRes.data);
      setActiveRoutes(activeRoutesRes.data);
      setLoans(loansRes.data);
      setBadWeather(weatherRes.data);
      
      // Check if game needs difficulty selection (no difficulty set means new game)
      if (!gameRes.data.difficulty) {
        setShowDifficultySelect(true);
      } else if (!gameRes.data.tutorial_seen) {
        setShowTutorial(true);
      }
      
      // Fetch certifications for hard mode
      if (gameRes.data.difficulty === 'hard') {
        try {
          const certsRes = await api.get('/certifications');
          setCertifications(certsRes.data);
        } catch (e) {
          // Ignore
        }
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        // 10 game minutes per real second (10/60 hours = 0.167 hours)
        await api.post('/game/advance-time?hours=0.167');
        await fetchData();
      } catch (error) {
        console.error('Error advancing time:', error);
      }
    }, 1000); // Every 1 second
    return () => clearInterval(interval);
  }, [fetchData]);

  useEffect(() => { fetchData(); }, [fetchData]);

  const onRefresh = useCallback(() => { setRefreshing(true); fetchData(); }, [fetchData]);

  const setHomeAirport = async (iata: string) => {
    try {
      await api.post('/game/home-airport', { iata });
      setShowHomeAirportModal(false);
      setAirportSearch('');
      fetchData();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to set home airport');
    }
  };

  const dismissTutorial = async () => {
    try {
      await api.post('/game/tutorial-seen');
      setShowTutorial(false);
      fetchData();
    } catch (error) {
      setShowTutorial(false);
    }
  };

  const startGameWithDifficulty = async () => {
    if (!selectedDifficulty || !selectedHomeAirport) {
      Alert.alert('Error', 'Please select a difficulty and home airport');
      return;
    }
    setStartingGame(true);
    try {
      await api.post('/game/start', {
        difficulty: selectedDifficulty,
        home_airport: selectedHomeAirport.iata
      });
      setShowDifficultySelect(false);
      setSelectedDifficulty('');
      setSelectedHomeAirport(null);
      setDifficultyAirportSearch('');
      fetchData();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to start game');
    } finally {
      setStartingGame(false);
    }
  };

  // Certification functions
  const startCertification = async (certId: string) => {
    setStartingCert(certId);
    try {
      const res = await api.post(`/certifications/${certId}/start`);
      Alert.alert('Training Started', res.data.message);
      fetchData();
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to start certification');
    } finally {
      setStartingCert(null);
    }
  };

  const completeCertification = async (certId: string) => {
    try {
      const res = await api.post(`/certifications/${certId}/complete`);
      if (res.data.complete) {
        Alert.alert('Congratulations!', res.data.message);
        fetchData();
      } else {
        Alert.alert('Still Training', res.data.message);
      }
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to complete certification');
    }
  };

  // Check if player can fly (has minimum certs)
  const canFly = () => {
    if (!gameState?.certifications) return true; // Easy/Medium mode
    const certs = gameState.certifications;
    return certs.commercial_pilot && certs.medical_certificate;
  };

  const purchaseAircraft = async () => {
    if (!selectedAircraft || !aircraftName) {
      Alert.alert('Error', 'Please select an aircraft and enter a name');
      return;
    }
    try {
      const payload: any = { aircraft_id: selectedAircraft.id, name: aircraftName, use_loan: useLoan };
      if (useLoan && loanAmount) {
        payload.loan_amount = parseInt(loanAmount);
        payload.loan_term = parseInt(loanTerm);
      }
      await api.post('/aircraft/purchase', payload);
      setShowAircraftModal(false);
      setSelectedAircraft(null);
      setAircraftName('');
      setUseLoan(false);
      setLoanAmount('');
      fetchData();
      Alert.alert('Success', 'Aircraft purchased successfully!');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to purchase aircraft');
    }
  };

  const sellAircraft = async () => {
    if (!aircraftToSell) return;
    try {
      const res = await api.delete(`/aircraft/owned/${aircraftToSell.id}`);
      setShowSellModal(false);
      setAircraftToSell(null);
      fetchData();
      Alert.alert('Success', res.data.message);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to sell aircraft');
    }
  };

  const cancelFlight = async (routeId: string) => {
    Alert.alert(
      'Cancel Flight',
      'Are you sure you want to cancel this flight? The aircraft will land at the nearest airport.',
      [
        { text: 'No', style: 'cancel' },
        {
          text: 'Yes, Cancel',
          style: 'destructive',
          onPress: async () => {
            try {
              const res = await api.delete(`/routes/${routeId}`);
              fetchData();
              Alert.alert('Flight Cancelled', `Aircraft landed at ${res.data.aircraft_landed_at}`);
            } catch (error: any) {
              Alert.alert('Error', error.response?.data?.detail || 'Failed to cancel flight');
            }
          }
        }
      ]
    );
  };

  const calculateProfit = async () => {
    if (!selectedPlane || !selectedOrigin || !selectedDestination) return;
    try {
      const res = await api.post('/routes/calculate-profit', {
        aircraft_id: selectedPlane.id,
        origin: selectedOrigin.iata,
        destination: selectedDestination.iata,
        flight_type: flightType,
        ticket_price: ticketPrice ? parseInt(ticketPrice) : undefined,
        cargo_rate: cargoRate ? parseInt(cargoRate) : undefined,
      });
      setEstimatedProfit(res.data);
      
      // Auto-fill the default price if not already set by user
      if (res.data.default_price) {
        if (flightType === 'passenger' && !ticketPrice) {
          setTicketPrice(res.data.default_price.toString());
        } else if (flightType === 'cargo' && !cargoRate) {
          setCargoRate(res.data.default_price.toString());
        }
      }
    } catch (error) {
      setEstimatedProfit(null);
    }
  };

  useEffect(() => {
    if (selectedPlane && selectedOrigin && selectedDestination) {
      calculateProfit();
    }
  }, [selectedPlane, selectedOrigin, selectedDestination, flightType, ticketPrice, cargoRate]);

  // Fetch weather for selected destination
  useEffect(() => {
    const fetchWeather = async () => {
      if (!selectedDestination) {
        setDestinationWeather(null);
        return;
      }
      try {
        const res = await api.get(`/weather/${selectedDestination.iata}`);
        setDestinationWeather(res.data);
      } catch (error) {
        setDestinationWeather(null);
      }
    };
    fetchWeather();
  }, [selectedDestination]);

  const createRoute = async () => {
    if (!selectedPlane || !selectedOrigin || !selectedDestination) {
      Alert.alert('Error', 'Please select aircraft, origin, and destination');
      return;
    }
    
    // Check certifications for hard mode
    if (gameState?.difficulty === 'hard') {
      const certs = gameState.certifications || {};
      if (!certs.commercial_pilot) {
        Alert.alert('Certification Required', 'You need a Commercial Pilot License (CPL) to fly for money. Complete your certifications first!');
        return;
      }
      if (!certs.medical_certificate) {
        Alert.alert('Certification Required', 'You need a valid Medical Certificate to fly.');
        return;
      }
    }
    
    // Check flight mode specific certifications
    if (gameState?.difficulty === 'hard') {
      const certs = gameState.certifications || {};
      if (flightMode === 'charter' && !certs.part_135) {
        Alert.alert('Certification Required', 'You need a Part 135 Air Carrier Certificate for charter flights. Complete your certifications first!');
        return;
      }
      if (flightMode === 'scheduled' && !certs.part_121) {
        Alert.alert('Certification Required', 'You need a Part 121 Air Carrier Certificate for scheduled flights. Complete your certifications first!');
        return;
      }
    }
    
    setScheduling(true);
    try {
      const payload: any = {
        aircraft_id: selectedPlane.id,
        origin: selectedOrigin.iata,
        destination: selectedDestination.iata,
        flight_type: flightType,
        flight_mode: flightMode,
      };
      if (flightType === 'passenger' && ticketPrice) payload.ticket_price = parseInt(ticketPrice);
      if (flightType === 'cargo' && cargoRate) payload.cargo_rate = parseInt(cargoRate);
      
      const response = await api.post('/routes', payload);
      setShowRouteModal(false);
      setSelectedPlane(null);
      setSelectedOrigin(null);
      setSelectedDestination(null);
      setTicketPrice('');
      setCargoRate('');
      setAirportSearch('');
      setEstimatedProfit(null);
      await fetchData();
      const route = response.data;
      const modeText = flightMode === 'scheduled' ? '(Scheduled - will return daily)' : '(Charter - one way)';
      Alert.alert('Flight Departed!', `${route.origin} → ${route.destination} ${modeText}\nDistance: ${Math.round(route.distance)} km\nDuration: ${route.flight_duration.toFixed(1)} hours`);
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create route');
    } finally {
      setScheduling(false);
    }
  };

  const createLoan = async (amount: number, term: number) => {
    try {
      await api.post('/loans', { amount, term_months: term });
      setShowLoanModal(false);
      setLoanAmount('');
      fetchData();
      Alert.alert('Success', 'Loan approved!');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to create loan');
    }
  };

  const payLoan = async () => {
    if (!selectedLoan || !paymentAmount) return;
    try {
      await api.post(`/loans/${selectedLoan.id}/pay`, { amount: parseInt(paymentAmount) });
      setShowLoanPaymentModal(false);
      setSelectedLoan(null);
      setPaymentAmount('');
      fetchData();
      Alert.alert('Success', 'Payment applied!');
    } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to make payment');
    }
  };

  const advanceDay = async () => {
    try { await api.post('/game/advance-day'); fetchData(); } catch (error: any) {
      Alert.alert('Error', error.response?.data?.detail || 'Failed to advance day');
    }
  };

  const resetGame = async () => {
    Alert.alert('Reset Game', 'Are you sure? All progress will be lost.', [
      { text: 'Cancel', style: 'cancel' },
      { text: 'Reset', style: 'destructive', onPress: async () => { await api.post('/game/reset'); fetchData(); } },
    ]);
  };

  const formatCurrency = (amount: number) => new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 0, maximumFractionDigits: 0 }).format(amount);
  const formatDate = (dateStr: string) => new Date(dateStr).toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });

  const filteredAirports = airports.filter(a =>
    a.iata.toLowerCase().includes(airportSearch.toLowerCase()) ||
    a.name.toLowerCase().includes(airportSearch.toLowerCase()) ||
    a.city.toLowerCase().includes(airportSearch.toLowerCase())
  );

  const availableAircraft = ownedAircraft.filter(a => a.status !== 'flying');

  const handleWebViewMessage = (event: any) => {
    try {
      const data = JSON.parse(event.nativeEvent.data);
      if (data.type === 'mapReady') {
        setMapInitialized(true);
        setTimeout(() => sendMapUpdate(), 100);
      }
      if (data.type === 'airport_click' && data.iata) {
        handleAirportClick(data.iata);
      }
    } catch (e) {
      // Ignore parse errors
    }
  };

  if (loading) {
    return (<View style={[styles.loadingContainer, {backgroundColor: colors.background}]}><ActivityIndicator size="large" color={colors.accent} /><Text style={[styles.loadingText, {color: colors.textSecondary}]}>Loading Airline Simulator...</Text></View>);
  }

  const renderHome = () => (
    <ScrollView style={[styles.tabContent, {backgroundColor: colors.background}]} refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.accent} />}>
      <View style={styles.header}>
        <Text style={[styles.headerTitle, {color: colors.text}]}>Airline Simulator</Text>
        <Text style={[styles.headerDate, {color: colors.textSecondary}]}>{gameState?.current_date ? formatDate(gameState.current_date) : ''}</Text>
      </View>
      
      {/* Difficulty Badge */}
      {gameState?.difficulty && (
        <View style={[styles.difficultyBadge, { 
          backgroundColor: gameState.difficulty === 'easy' ? '#4CAF50' : gameState.difficulty === 'medium' ? '#FF9800' : '#F44336' 
        }]}>
          <Text style={styles.difficultyBadgeText}>{gameState.difficulty.toUpperCase()} MODE</Text>
        </View>
      )}
      
      <View style={[styles.balanceCard, {backgroundColor: colors.card}]}>
        <Text style={[styles.balanceLabel, {color: colors.textSecondary}]}>Balance</Text>
        <Text style={[styles.balanceAmount, {color: colors.success}]}>{formatCurrency(gameState?.balance || 0)}</Text>
      </View>
      <View style={styles.statsRow}>
        <View style={[styles.statCard, {backgroundColor: colors.card, borderColor: colors.border}]}><Ionicons name="airplane" size={20} color={colors.accent} /><Text style={[styles.statValue, {color: colors.text}]}>{ownedAircraft.length}</Text><Text style={[styles.statLabel, {color: colors.textSecondary}]}>Fleet</Text></View>
        <View style={[styles.statCard, {backgroundColor: colors.card, borderColor: colors.border}]}><Ionicons name="checkmark-circle" size={20} color={colors.success} /><Text style={[styles.statValue, {color: colors.text}]}>{gameState?.flights_completed || 0}</Text><Text style={[styles.statLabel, {color: colors.textSecondary}]}>Flights</Text></View>
        <View style={[styles.statCard, {backgroundColor: colors.card, borderColor: colors.border}]}><Ionicons name="trending-up" size={20} color={colors.warning} /><Text style={[styles.statValue, {color: colors.text}]}>{activeRoutes.length}</Text><Text style={[styles.statLabel, {color: colors.textSecondary}]}>Active</Text></View>
      </View>
      {gameState?.home_airport && (<View style={[styles.homeAirportCard, {backgroundColor: colors.card}]}><Ionicons name="home" size={18} color={colors.accent} /><Text style={[styles.homeAirportText, {color: colors.text}]}>Home: {gameState.home_airport}</Text></View>)}
      
      {/* Certifications Section (Hard Mode) */}
      {gameState?.difficulty === 'hard' && certifications.length > 0 && (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, {color: colors.text}]}>FAA Certifications</Text>
          <Text style={[styles.sectionSubtitle, {color: colors.textSecondary}]}>Complete all to operate your airline</Text>
          {certifications.map(cert => (
            <View key={cert.id} style={[styles.certCard, {backgroundColor: colors.card, borderColor: colors.border}, cert.completed && styles.certCardComplete]}>
              <View style={styles.certHeader}>
                <Ionicons name={cert.completed ? "checkmark-circle" : cert.in_progress ? "time" : cert.available ? "document-text" : "lock-closed"} size={20} color={cert.completed ? colors.success : cert.in_progress ? colors.warning : cert.available ? colors.accent : colors.textMuted} />
                <View style={styles.certInfo}>
                  <Text style={[styles.certName, {color: colors.text}, cert.completed && {color: colors.success}]}>{cert.name}</Text>
                  <Text style={[styles.certForm, {color: colors.textSecondary}]}>{cert.form}</Text>
                </View>
                <Text style={[styles.certCost, {color: colors.text}, cert.completed && {color: colors.success}]}>{cert.completed ? '✓' : formatCurrency(cert.cost)}</Text>
              </View>
              <Text style={[styles.certDesc, {color: colors.textSecondary}]}>{cert.description}</Text>
              <Text style={[styles.certUnlocks, {color: colors.success}]}>Unlocks: {cert.unlocks}</Text>
              {cert.prerequisites.length > 0 && !cert.completed && (
                <Text style={[styles.certPrereqs, {color: colors.warning}]}>Requires: {cert.prerequisites.map(p => certifications.find(c => c.id === p)?.name || p).join(', ')}</Text>
              )}
              {!cert.completed && (
                <View style={styles.certActions}>
                  {cert.in_progress ? (
                    <View style={styles.certTraining}>
                      <ActivityIndicator size="small" color={colors.warning} />
                      <Text style={[styles.certTrainingText, {color: colors.warning}]}>{Math.ceil(cert.training_remaining)}s remaining</Text>
                      <TouchableOpacity style={[styles.certCompleteBtn, {backgroundColor: colors.success}]} onPress={() => completeCertification(cert.id)}>
                        <Text style={styles.certBtnText}>Check</Text>
                      </TouchableOpacity>
                    </View>
                  ) : cert.available ? (
                    <TouchableOpacity 
                      style={[styles.certStartBtn, {backgroundColor: colors.accent}]} 
                      onPress={() => startCertification(cert.id)}
                      disabled={startingCert === cert.id}
                    >
                      {startingCert === cert.id ? (
                        <ActivityIndicator size="small" color="#FFF" />
                      ) : (
                        <Text style={styles.certBtnText}>Start ({cert.time_seconds}s)</Text>
                      )}
                    </TouchableOpacity>
                  ) : (
                    <Text style={[styles.certLocked, {color: colors.textMuted}]}>Complete prerequisites first</Text>
                  )}
                </View>
              )}
            </View>
          ))}
        </View>
      )}
      
      {activeRoutes.length > 0 && (
        <View style={styles.section}>
          <Text style={[styles.sectionTitle, {color: colors.text}]}>Active Flights</Text>
          {activeRoutes.map(route => (
            <View key={route.id} style={[styles.flightCard, {backgroundColor: colors.card}]}>
              <View style={styles.flightHeader}><Text style={[styles.flightRoute, {color: colors.text}]}>{route.origin} → {route.destination}</Text><Text style={[styles.flightProgress, {color: colors.accent}]}>{Math.round(route.progress * 100)}%</Text></View>
              <View style={[styles.progressBar, {backgroundColor: colors.surfaceDark}]}><View style={[styles.progressFill, { width: `${route.progress * 100}%`, backgroundColor: colors.accent }]} /></View>
              <Text style={[styles.flightInfo, {color: colors.textSecondary}]}>{route.aircraft_name} • {route.flight_type === 'passenger' ? `${route.passengers} pax` : `${route.cargo_weight}kg`}</Text>
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );

  const renderMap = () => {
    return (
      <View style={styles.mapContainer}>
        {Platform.OS === 'web' ? (
          <iframe 
            ref={iframeRef as any}
            srcDoc={staticMapHtml} 
            style={{ flex: 1, border: 'none', width: '100%', height: '100%' } as any} 
          />
        ) : (
          <WebView 
            ref={webviewRef}
            source={{ html: staticMapHtml }} 
            style={styles.map} 
            javaScriptEnabled={true} 
            domStorageEnabled={true} 
            onMessage={handleWebViewMessage}
          />
        )}
        <View style={styles.mapPanel}>
          {availableAircraft.length === 0 ? (
            <View style={styles.mapPanelEmpty}><Text style={styles.mapPanelEmptyText}>Purchase an aircraft first</Text></View>
          ) : (
            <>
              <Text style={styles.mapInstruction}>1. Select plane, 2. Tap airport dot on map for destination</Text>
              <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.mapAircraftList}>
                {availableAircraft.map(aircraft => (
                  <TouchableOpacity key={aircraft.id} style={[styles.mapAircraftItem, selectedPlane?.id === aircraft.id && styles.mapAircraftItemSelected]} onPress={() => {
                    setSelectedPlane(aircraft);
                    const origin = airports.find(a => a.iata === aircraft.current_airport);
                    if (origin) setSelectedOrigin(origin);
                    setSelectedDestination(null);
                  }}>
                    <Text style={[styles.mapAircraftName, selectedPlane?.id === aircraft.id && {color:'#FFF'}]}>{aircraft.name}</Text>
                    <Text style={styles.mapAircraftLoc}>{aircraft.current_airport}</Text>
                  </TouchableOpacity>
                ))}
              </ScrollView>
              {selectedPlane && (
                <View style={styles.mapRouteInfo}>
                  <View style={styles.mapRouteRow}>
                    <Text style={styles.mapLabel}>From: <Text style={{color:'#4CAF50',fontWeight:'bold'}}>{selectedOrigin?.iata || '-'}</Text></Text>
                    <TouchableOpacity style={styles.destSelectBtn} onPress={() => setShowRouteModal(true)}>
                      <Text style={styles.destSelectText}>To: {selectedDestination?.iata || 'Select...'}</Text>
                      <Ionicons name="chevron-down" size={14} color="#4A90E2" />
                    </TouchableOpacity>
                    <Text style={styles.mapLabel}>Range: {selectedPlane.details?.range}km</Text>
                  </View>
                  {selectedDestination && (
                    <>
                      {/* Weather Widget */}
                      {destinationWeather && (
                        <View style={styles.weatherWidget}>
                          <View style={styles.weatherWidgetHeader}>
                            <Ionicons 
                              name={
                                destinationWeather.condition === 'clear' ? 'sunny' :
                                destinationWeather.condition === 'cloudy' ? 'cloudy' :
                                destinationWeather.condition === 'rain' ? 'rainy' :
                                destinationWeather.condition === 'storm' ? 'thunderstorm' :
                                destinationWeather.condition === 'fog' ? 'cloud' :
                                destinationWeather.condition === 'snow' ? 'snow' : 'partly-sunny'
                              } 
                              size={16} 
                              color={
                                destinationWeather.condition === 'clear' ? '#4CAF50' :
                                destinationWeather.condition === 'storm' ? '#F44336' :
                                destinationWeather.condition === 'fog' ? '#9E9E9E' : '#FF9800'
                              } 
                            />
                            <Text style={styles.weatherWidgetText}>{selectedDestination.iata} Weather: {destinationWeather.condition}</Text>
                          </View>
                          <View style={styles.weatherWidgetDetails}>
                            <Text style={styles.weatherWidgetDetail}>Wind: {destinationWeather.wind_speed}km/h</Text>
                            <Text style={styles.weatherWidgetDetail}>Vis: {destinationWeather.visibility}km</Text>
                            <Text style={styles.weatherWidgetDetail}>{destinationWeather.temperature}°C</Text>
                            {destinationWeather.delay_hours > 0 && (
                              <Text style={[styles.weatherWidgetDetail, {color: '#FF9800'}]}>+{destinationWeather.delay_hours.toFixed(1)}h delay</Text>
                            )}
                          </View>
                        </View>
                      )}
                      
                      {/* Fuel Info Widget */}
                      {estimatedProfit && estimatedProfit.fuel_type && (
                        <View style={styles.fuelWidget}>
                          <Ionicons name="flame" size={14} color="#FF9800" />
                          <Text style={styles.fuelWidgetText}>
                            {estimatedProfit.fuel_type}: {estimatedProfit.fuel_liters}L @ ${estimatedProfit.fuel_price_per_liter}/L = {formatCurrency(estimatedProfit.fuel_cost)}
                          </Text>
                        </View>
                      )}
                      
                      <View style={styles.mapTypeRow}>
                        <TouchableOpacity style={[styles.mapTypeBtn, flightType === 'passenger' && styles.mapTypeBtnActive]} onPress={() => setFlightType('passenger')}>
                          <Text style={[styles.mapTypeText, flightType === 'passenger' && {color:'#FFF'}]}>Passenger</Text>
                        </TouchableOpacity>
                        <TouchableOpacity style={[styles.mapTypeBtn, flightType === 'cargo' && styles.mapTypeBtnActive]} onPress={() => setFlightType('cargo')}>
                          <Text style={[styles.mapTypeText, flightType === 'cargo' && {color:'#FFF'}]}>Cargo</Text>
                        </TouchableOpacity>
                      </View>
                      <View style={styles.mapModeRow}>
                        <TouchableOpacity 
                          style={[styles.mapModeBtn, flightMode === 'charter' && styles.mapModeBtnActive, gameState?.difficulty === 'hard' && !gameState?.certifications?.part_135 && styles.mapModeBtnLocked]} 
                          onPress={() => setFlightMode('charter')}
                        >
                          <Ionicons name="airplane" size={14} color={flightMode === 'charter' ? '#FFF' : '#4A90E2'} />
                          <Text style={[styles.mapModeText, flightMode === 'charter' && {color:'#FFF'}]}>Charter</Text>
                          {gameState?.difficulty === 'hard' && !gameState?.certifications?.part_135 && <Ionicons name="lock-closed" size={10} color="#F44336" />}
                        </TouchableOpacity>
                        <TouchableOpacity 
                          style={[styles.mapModeBtn, flightMode === 'scheduled' && styles.mapModeBtnActive, gameState?.difficulty === 'hard' && !gameState?.certifications?.part_121 && styles.mapModeBtnLocked]} 
                          onPress={() => setFlightMode('scheduled')}
                        >
                          <Ionicons name="calendar" size={14} color={flightMode === 'scheduled' ? '#FFF' : '#FF9800'} />
                          <Text style={[styles.mapModeText, flightMode === 'scheduled' && {color:'#FFF'}]}>Scheduled</Text>
                          {gameState?.difficulty === 'hard' && !gameState?.certifications?.part_121 && <Ionicons name="lock-closed" size={10} color="#F44336" />}
                        </TouchableOpacity>
                      </View>
                      <Text style={styles.mapModeHint}>{flightMode === 'charter' ? 'One-way: plane stays at destination' : 'Daily round-trip: A→B→A repeating'}</Text>
                      <View style={styles.mapPriceRow}>
                        <TextInput style={styles.mapPriceInput} placeholder={flightType === 'passenger' ? "Ticket $" : "Rate/kg"} placeholderTextColor="#666" value={flightType === 'passenger' ? ticketPrice : cargoRate} onChangeText={flightType === 'passenger' ? setTicketPrice : setCargoRate} keyboardType="numeric" />
                        {estimatedProfit && (
                          <Text style={[styles.mapProfitText, {color: estimatedProfit.is_profitable ? '#4CAF50' : '#F44336'}]}>
                            Est: {formatCurrency(estimatedProfit.estimated_profit)}
                          </Text>
                        )}
                      </View>
                      <TouchableOpacity style={styles.mapStartBtn} onPress={createRoute} disabled={scheduling}>
                        {scheduling ? <ActivityIndicator size="small" color="#FFF" /> : <><Ionicons name="send" size={16} color="#FFF" /><Text style={styles.mapStartText}>Start {flightMode === 'scheduled' ? 'Scheduled' : 'Charter'} Flight</Text></>}
                      </TouchableOpacity>
                    </>
                  )}
                </View>
              )}
            </>
          )}
        </View>
      </View>
    );
  };

  const renderAircraft = () => (
    <ScrollView style={styles.tabContent}>
      <View style={styles.sectionHeader}><Text style={styles.sectionTitle}>Your Fleet</Text><TouchableOpacity style={styles.addBtn} onPress={() => setShowAircraftModal(true)}><Ionicons name="add" size={20} color="#FFF" /></TouchableOpacity></View>
      {ownedAircraft.length === 0 ? (
        <View style={styles.emptyState}><Ionicons name="airplane-outline" size={40} color="#666" /><Text style={styles.emptyText}>No aircraft yet</Text></View>
      ) : (
        ownedAircraft.map(aircraft => (
          <View key={aircraft.id} style={styles.aircraftCard}>
            <View style={styles.aircraftHeader}>
              <Text style={styles.aircraftName}>{aircraft.name}</Text>
              <View style={[styles.statusBadge, { backgroundColor: aircraft.status === 'flying' ? '#4CAF50' : '#666' }]}><Text style={styles.statusText}>{aircraft.status}</Text></View>
            </View>
            <Text style={styles.aircraftModel}>{aircraft.details?.brand} {aircraft.details?.model}</Text>
            <View style={styles.aircraftStats}>
              <Text style={styles.aircraftStatText}>Cap: {aircraft.details?.capacity}</Text>
              <Text style={styles.aircraftStatText}>Range: {aircraft.details?.range}km</Text>
              <Text style={styles.aircraftStatText}>@ {aircraft.current_airport}</Text>
            </View>
            {aircraft.status !== 'flying' && (
              <TouchableOpacity style={styles.sellBtn} onPress={() => { setAircraftToSell(aircraft); setShowSellModal(true); }}>
                <Text style={styles.sellBtnText}>Sell (70%)</Text>
              </TouchableOpacity>
            )}
          </View>
        ))
      )}
      <Text style={styles.sectionTitle}>Aircraft Store</Text>
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.brandFilter}>
        <TouchableOpacity style={[styles.brandChip, !selectedBrand && styles.brandChipActive]} onPress={() => setSelectedBrand('')}><Text style={[styles.brandChipText, !selectedBrand && {color:'#FFF'}]}>All</Text></TouchableOpacity>
        {Object.keys(aircraftDatabase).map(brand => (
          <TouchableOpacity key={brand} style={[styles.brandChip, selectedBrand === brand && styles.brandChipActive]} onPress={() => setSelectedBrand(brand)}><Text style={[styles.brandChipText, selectedBrand === brand && {color:'#FFF'}]}>{brand}</Text></TouchableOpacity>
        ))}
      </ScrollView>
      {Object.entries(aircraftDatabase).filter(([brand]) => !selectedBrand || brand === selectedBrand).map(([brand, aircraft]) => (
        <View key={brand}>
          <Text style={styles.brandTitle}>{brand}</Text>
          {aircraft.map(plane => (
            <TouchableOpacity key={plane.id} style={styles.storeCard} onPress={() => { setSelectedAircraft(plane); setUseLoan(true); const needed = Math.max(0, plane.price - (gameState?.balance || 0)); setLoanAmount(needed > 0 ? needed.toString() : ''); setShowAircraftModal(true); }}>
              <View style={styles.storeCardHeader}><Text style={styles.storeCardTitle}>{plane.model}</Text><Text style={styles.storeCardPrice}>{formatCurrency(plane.price)}</Text></View>
              <Text style={styles.storeCardStats}>Cap: {plane.capacity} | Range: {plane.range}km | {plane.cruise_speed}km/h</Text>
            </TouchableOpacity>
          ))}
        </View>
      ))}
    </ScrollView>
  );

  const renderRoutes = () => (
    <ScrollView style={[styles.tabContent, {backgroundColor: colors.background}]}>
      <Text style={[styles.sectionTitle, {color: colors.text}]}>Flight History</Text>
      {allRoutes.length === 0 ? (
        <View style={styles.emptyState}><Ionicons name="navigate-outline" size={40} color={colors.textMuted} /><Text style={[styles.emptyText, {color: colors.textSecondary}]}>No flights yet</Text></View>
      ) : (
        allRoutes.map(route => (
          <View key={route.id} style={[styles.routeCard, {backgroundColor: colors.card}]}>
            <View style={styles.routeHeader}>
              <Text style={[styles.routeTitle, {color: colors.text}]}>{route.origin} → {route.destination}</Text>
              <View style={{flexDirection:'row',alignItems:'center'}}>
                <View style={[styles.statusBadge, { backgroundColor: route.status === 'completed' ? colors.success : route.status === 'in_progress' ? colors.warning : colors.textMuted }]}><Text style={styles.statusText}>{route.status.replace('_',' ')}</Text></View>
                {route.status === 'in_progress' && (
                  <TouchableOpacity style={styles.cancelFlightBtn} onPress={() => cancelFlight(route.id)}>
                    <Ionicons name="close-circle" size={20} color={colors.danger} />
                  </TouchableOpacity>
                )}
              </View>
            </View>
            {route.status === 'in_progress' && (<View style={[styles.progressBar, {backgroundColor: colors.surfaceDark}]}><View style={[styles.progressFill, { width: `${route.progress * 100}%`, backgroundColor: route.delayed ? colors.warning : colors.accent }]} /></View>)}
            
            {/* Show delay/diversion info */}
            {route.delayed && (
              <View style={[styles.alertBanner, {backgroundColor: colors.warning + '20', borderColor: colors.warning}]}>
                <Ionicons name="time" size={14} color={colors.warning} />
                <Text style={{color: colors.warning, fontSize: 11, marginLeft: 4}}>
                  DELAYED: {route.delay_reason} | Compensation: {formatCurrency(route.delay_compensation || 0)}
                </Text>
              </View>
            )}
            {route.diverted_to && (
              <View style={[styles.alertBanner, {backgroundColor: colors.danger + '20', borderColor: colors.danger}]}>
                <Ionicons name="warning" size={14} color={colors.danger} />
                <Text style={{color: colors.danger, fontSize: 11, marginLeft: 4}}>
                  DIVERTED to {route.diverted_to}: {route.diversion_reason} | Compensation: {formatCurrency(route.diversion_compensation || 0)}
                </Text>
              </View>
            )}
            {route.total_compensation > 0 && route.status === 'completed' && (
              <View style={[styles.alertBanner, {backgroundColor: colors.textMuted + '20', borderColor: colors.textMuted}]}>
                <Ionicons name="cash" size={14} color={colors.textMuted} />
                <Text style={{color: colors.textMuted, fontSize: 11, marginLeft: 4}}>
                  Passenger compensation paid: {formatCurrency(route.total_compensation)}
                </Text>
              </View>
            )}
            
            <View style={styles.routeStats}><Text style={[styles.routeStat, {color: colors.textSecondary}]}>{Math.round(route.distance)}km</Text><Text style={[styles.routeStat, {color: colors.textSecondary}]}>{route.flight_duration.toFixed(1)}h</Text><Text style={[styles.routeStat, {color: colors.textSecondary}]}>{route.flight_type}</Text><Text style={[styles.routeStat, {color: colors.textSecondary}]}>{route.flight_mode || 'charter'}</Text>{route.turnaround_hours && <Text style={[styles.routeStat, {color: colors.accent}]}>Next: {route.turnaround_hours}h</Text>}</View>
            <View style={[styles.routeFinancials, {borderTopColor: colors.border}]}>
              <Text style={{color: colors.success, fontSize:12}}>Rev: {formatCurrency(route.revenue)}</Text>
              <Text style={{color: colors.danger, fontSize:12}}>Cost: {formatCurrency(route.costs)}</Text>
              <Text style={{color: route.revenue - route.costs > 0 ? colors.success : colors.danger, fontSize:12, fontWeight:'600'}}>Profit: {formatCurrency(route.revenue - route.costs)}</Text>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );

  const renderWeather = () => (
    <ScrollView style={styles.tabContent}>
      <Text style={styles.sectionTitle}>Weather Alerts</Text>
      <Text style={styles.weatherNote}>Updates every simulation hour. Poor weather adds delays and costs.</Text>
      {badWeather.length === 0 ? (
        <View style={styles.emptyState}><Ionicons name="sunny" size={40} color="#4CAF50" /><Text style={styles.emptyText}>All clear!</Text></View>
      ) : (
        badWeather.map((item, i) => (
          <View key={i} style={styles.weatherCard}>
            <View style={styles.weatherHeader}>
              <Text style={styles.weatherAirport}>{item.iata} - {item.city}</Text>
              <View style={[styles.weatherBadge, { backgroundColor: item.weather.condition === 'storm' ? '#F44336' : item.weather.condition === 'fog' ? '#9E9E9E' : '#FF9800' }]}>
                <Text style={styles.weatherBadgeText}>{item.weather.condition}</Text>
              </View>
            </View>
            <View style={styles.weatherDetails}>
              <Text style={styles.weatherDetail}>Wind: {item.weather.wind_speed}km/h</Text>
              <Text style={styles.weatherDetail}>Visibility: {item.weather.visibility}km</Text>
              <Text style={styles.weatherDetail}>Delay: +{item.weather.delay_hours.toFixed(1)}h</Text>
              <Text style={styles.weatherDetail}>Cost: +{item.weather.extra_cost_percent}%</Text>
            </View>
          </View>
        ))
      )}
    </ScrollView>
  );

  const renderFinances = () => (
    <ScrollView style={[styles.tabContent, {backgroundColor: colors.background}]}>
      <View style={[styles.financeCard, {backgroundColor: colors.card}]}><Text style={[styles.financeLabel, {color: colors.textSecondary}]}>Total Revenue</Text><Text style={[styles.financeValue, {color: colors.success}]}>{formatCurrency(gameState?.total_revenue || 0)}</Text></View>
      <View style={[styles.financeCard, {backgroundColor: colors.card}]}><Text style={[styles.financeLabel, {color: colors.textSecondary}]}>Total Expenses</Text><Text style={[styles.financeValue, {color: colors.danger}]}>{formatCurrency(gameState?.total_expenses || 0)}</Text></View>
      <View style={[styles.financeCard, {backgroundColor: colors.card}]}><Text style={[styles.financeLabel, {color: colors.textSecondary}]}>Net Profit</Text><Text style={[styles.financeValue, {color: (gameState?.total_revenue || 0) - (gameState?.total_expenses || 0) > 0 ? colors.success : colors.danger}]}>{formatCurrency((gameState?.total_revenue || 0) - (gameState?.total_expenses || 0))}</Text></View>
      <View style={styles.sectionHeader}><Text style={[styles.sectionTitle, {color: colors.text}]}>Loans</Text><TouchableOpacity style={[styles.addBtn, {backgroundColor: colors.accent}]} onPress={() => setShowLoanModal(true)}><Ionicons name="add" size={20} color="#FFF" /></TouchableOpacity></View>
      {loans.length === 0 ? (
        <View style={styles.emptyState}><Ionicons name="card-outline" size={40} color={colors.textMuted} /><Text style={[styles.emptyText, {color: colors.textSecondary}]}>No loans</Text></View>
      ) : (
        loans.map(loan => (
          <View key={loan.id} style={[styles.loanCard, {backgroundColor: colors.card}]}>
            <View style={styles.loanHeader}><Text style={[styles.loanAmount, {color: colors.text}]}>{formatCurrency(loan.amount)}</Text><Text style={[styles.loanRate, {color: colors.warning}]}>7% APR</Text></View>
            <Text style={[styles.loanDetail, {color: colors.textSecondary}]}>Remaining: {formatCurrency(loan.remaining)} | Monthly: {formatCurrency(loan.monthly_payment)}</Text>
            <View style={[styles.progressBar, {backgroundColor: colors.surfaceDark}]}><View style={[styles.progressFill, { width: `${(1 - loan.remaining / loan.amount) * 100}%`, backgroundColor: colors.success }]} /></View>
            {loan.remaining > 0 && (
              <TouchableOpacity style={[styles.payBtn, {backgroundColor: colors.accent}]} onPress={() => { setSelectedLoan(loan); setPaymentAmount(''); setShowLoanPaymentModal(true); }}>
                <Text style={styles.payBtnText}>Make Payment</Text>
              </TouchableOpacity>
            )}
          </View>
        ))
      )}
    </ScrollView>
  );

  const renderSettings = () => (
    <ScrollView style={[styles.tabContent, {backgroundColor: colors.background}]}>
      <Text style={[styles.sectionTitle, {color: colors.text}]}>Settings</Text>
      
      {/* Theme Toggle */}
      <TouchableOpacity 
        style={[styles.settingsItem, {backgroundColor: colors.card}]}
        onPress={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
      >
        <Ionicons name={theme === 'dark' ? 'moon' : 'sunny'} size={20} color={colors.accent} />
        <Text style={[styles.settingsText, {color: colors.text}]}>Theme</Text>
        <View style={{flex: 1}} />
        <View style={[styles.themeToggle, {backgroundColor: colors.input}]}>
          <View style={[
            styles.themeToggleBtn, 
            {backgroundColor: colors.accent},
            theme === 'light' && {marginLeft: 24}
          ]}>
            <Ionicons name={theme === 'dark' ? 'moon' : 'sunny'} size={14} color="#FFF" />
          </View>
        </View>
      </TouchableOpacity>
      
      <TouchableOpacity style={[styles.settingsItem, {backgroundColor: colors.card}]} onPress={() => setShowTutorial(true)}>
        <Ionicons name="help-circle" size={20} color={colors.accent} />
        <Text style={[styles.settingsText, {color: colors.text}]}>View Tutorial</Text>
      </TouchableOpacity>
      <TouchableOpacity style={[styles.settingsItem, {backgroundColor: colors.card}]} onPress={resetGame}>
        <Ionicons name="refresh" size={20} color={colors.danger} />
        <Text style={[styles.settingsText, {color: colors.danger}]}>Reset Game</Text>
      </TouchableOpacity>
      <View style={[styles.settingsInfo, {backgroundColor: colors.card}]}>
        <Text style={[styles.settingsInfoText, {color: colors.textSecondary}]}>Version 1.0</Text>
        <Text style={[styles.settingsInfoText, {color: colors.textSecondary}]}>Time: 1 sec = 10 min</Text>
        <Text style={[styles.settingsInfoText, {color: colors.textSecondary}]}>Theme: {theme === 'dark' ? 'Dark Mode' : 'Light Mode'}</Text>
      </View>
    </ScrollView>
  );

  return (
    <SafeAreaView style={[styles.container, {backgroundColor: colors.background}]}>
      <KeyboardAvoidingView style={{flex:1}} behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
        <TouchableWithoutFeedback onPress={Keyboard.dismiss} accessible={false}>
          <View style={[styles.content, {backgroundColor: colors.background}, keyboardVisible && {marginBottom: 100}]}>
            {activeTab === 'home' && renderHome()}
            {activeTab === 'map' && renderMap()}
            {activeTab === 'aircraft' && renderAircraft()}
            {activeTab === 'routes' && renderRoutes()}
            {activeTab === 'weather' && renderWeather()}
            {activeTab === 'finances' && renderFinances()}
            {activeTab === 'settings' && renderSettings()}
          </View>
        </TouchableWithoutFeedback>
      </KeyboardAvoidingView>

      <View style={[styles.tabBar, {backgroundColor: colors.tabBar, borderTopColor: colors.border}]}>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={styles.tabBarContent}>
          {TABS.map(tab => (
            <TouchableOpacity key={tab.id} style={[styles.tabItem, activeTab === tab.id && styles.tabItemActive]} onPress={() => { setActiveTab(tab.id); Keyboard.dismiss(); }}>
              <Ionicons name={tab.icon as any} size={20} color={activeTab === tab.id ? colors.accent : colors.textMuted} />
              <Text style={[styles.tabLabel, {color: colors.textMuted}, activeTab === tab.id && {color: colors.accent}]}>{tab.label}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>

      {/* Difficulty Selection Modal */}
      <Modal visible={showDifficultySelect} animationType="fade" transparent>
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.modalOverlay}>
            <View style={styles.difficultyContent}>
            <Text style={styles.difficultyTitle}>Select Difficulty</Text>
            
            <View style={styles.difficultyOptions}>
              <TouchableOpacity 
                style={[styles.difficultyCard, selectedDifficulty === 'easy' && styles.difficultyCardSelected]}
                onPress={() => setSelectedDifficulty('easy')}
              >
                <Ionicons name="sunny" size={32} color={selectedDifficulty === 'easy' ? '#FFF' : '#4CAF50'} />
                <Text style={[styles.difficultyName, selectedDifficulty === 'easy' && {color: '#FFF'}]}>Easy</Text>
                <Text style={styles.difficultyDesc}>Cessna 172 + $15,000</Text>
                <Text style={styles.difficultyDesc}>Great for beginners</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.difficultyCard, selectedDifficulty === 'medium' && styles.difficultyCardSelected]}
                onPress={() => setSelectedDifficulty('medium')}
              >
                <Ionicons name="partly-sunny" size={32} color={selectedDifficulty === 'medium' ? '#FFF' : '#FF9800'} />
                <Text style={[styles.difficultyName, selectedDifficulty === 'medium' && {color: '#FFF'}]}>Medium</Text>
                <Text style={styles.difficultyDesc}>Cessna 172 + $0</Text>
                <Text style={styles.difficultyDesc}>Standard challenge</Text>
              </TouchableOpacity>
              
              <TouchableOpacity 
                style={[styles.difficultyCard, selectedDifficulty === 'hard' && styles.difficultyCardSelected]}
                onPress={() => setSelectedDifficulty('hard')}
              >
                <Ionicons name="thunderstorm" size={32} color={selectedDifficulty === 'hard' ? '#FFF' : '#F44336'} />
                <Text style={[styles.difficultyName, selectedDifficulty === 'hard' && {color: '#FFF'}]}>Hard</Text>
                <Text style={styles.difficultyDesc}>No plane, No money</Text>
                <Text style={styles.difficultyDesc}>Get pilot license first</Text>
                <Text style={styles.difficultyDesc}>($10k, 30 seconds)</Text>
              </TouchableOpacity>
            </View>
            
            {selectedDifficulty && (
              <View style={styles.difficultyAirportSection}>
                <Text style={styles.difficultySubtitle}>Select Home Airport</Text>
                <TextInput 
                  style={styles.searchInput} 
                  placeholder="Search airports..." 
                  placeholderTextColor="#666" 
                  value={difficultyAirportSearch} 
                  onChangeText={setDifficultyAirportSearch} 
                />
                <FlatList 
                  data={airports.filter(a => 
                    difficultyAirportSearch === '' || 
                    a.iata.toLowerCase().includes(difficultyAirportSearch.toLowerCase()) ||
                    a.city.toLowerCase().includes(difficultyAirportSearch.toLowerCase())
                  ).slice(0, 8)} 
                  keyExtractor={item => item.iata} 
                  renderItem={({ item }) => (
                    <TouchableOpacity 
                      style={[styles.airportItem, selectedHomeAirport?.iata === item.iata && styles.airportItemSelected]} 
                      onPress={() => setSelectedHomeAirport(item)}
                    >
                      <Text style={styles.airportCode}>{item.iata}</Text>
                      <Text style={styles.airportName}>{item.city}, {item.country}</Text>
                    </TouchableOpacity>
                  )} 
                  style={{maxHeight: 200}} 
                />
              </View>
            )}
            
            {selectedDifficulty && selectedHomeAirport && (
              <TouchableOpacity 
                style={styles.startGameBtn} 
                onPress={startGameWithDifficulty}
                disabled={startingGame}
              >
                {startingGame ? (
                  <ActivityIndicator size="small" color="#FFF" />
                ) : (
                  <Text style={styles.startGameText}>Start Game</Text>
                )}
              </TouchableOpacity>
            )}
          </View>
        </View>
        </TouchableWithoutFeedback>
      </Modal>

      {/* Tutorial Modal */}
      <Modal visible={showTutorial} animationType="fade" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.tutorialContent}>
            {gameState?.difficulty === 'easy' && (
              <>
                <Text style={styles.tutorialTitle}>Easy Mode - Welcome!</Text>
                <View style={styles.tutorialItem}><Ionicons name="checkmark-circle" size={20} color="#4CAF50" /><Text style={styles.tutorialText}>You start with a Cessna 172 + $15,000</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="checkmark-circle" size={20} color="#4CAF50" /><Text style={styles.tutorialText}>All certifications already complete</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="time" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Time: 10 seconds = 1 hour in-game</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="map" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Go to Map tab to schedule flights</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="cash" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Take loans to buy bigger planes</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="trending-up" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Tip: Ticket prices auto-set for $500+ profit</Text></View>
              </>
            )}
            {gameState?.difficulty === 'medium' && (
              <>
                <Text style={styles.tutorialTitle}>Medium Mode - Challenge!</Text>
                <View style={styles.tutorialItem}><Ionicons name="airplane" size={20} color="#FF9800" /><Text style={styles.tutorialText}>You start with a Cessna 172 but $0 cash</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="checkmark-circle" size={20} color="#4CAF50" /><Text style={styles.tutorialText}>All certifications already complete</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="cash" size={20} color="#FF9800" /><Text style={styles.tutorialText}>Fly routes to earn money first!</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="map" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Go to Map tab to schedule flights</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="card" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Use Finance tab to take loans if needed</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="trending-up" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Tip: Short routes = quick cash flow</Text></View>
              </>
            )}
            {gameState?.difficulty === 'hard' && (
              <>
                <Text style={styles.tutorialTitle}>Hard Mode - Realistic!</Text>
                <View style={styles.tutorialItem}><Ionicons name="warning" size={20} color="#F44336" /><Text style={styles.tutorialText}>No plane, no money - start from zero!</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="school" size={20} color="#F44336" /><Text style={styles.tutorialText}>Must complete FAA certifications first</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="document-text" size={20} color="#FF9800" /><Text style={styles.tutorialText}>Start: Medical → PPL → IFR → CPL</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="card" size={20} color="#FF9800" /><Text style={styles.tutorialText}>Take a loan to fund certifications (~$55k)</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="airplane" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Need Commercial Pilot License to fly for $</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="business" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Part 135/121 certs unlock charter & airline ops</Text></View>
              </>
            )}
            {!gameState?.difficulty && (
              <>
                <Text style={styles.tutorialTitle}>Welcome to Airline Simulator!</Text>
                <View style={styles.tutorialItem}><Ionicons name="time" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Time: 10 seconds = 1 hour</Text></View>
                <View style={styles.tutorialItem}><Ionicons name="airplane" size={20} color="#4A90E2" /><Text style={styles.tutorialText}>Build your airline empire!</Text></View>
              </>
            )}
            <TouchableOpacity style={styles.tutorialBtn} onPress={dismissTutorial}><Text style={styles.tutorialBtnText}>Got it!</Text></TouchableOpacity>
          </View>
        </View>
      </Modal>

      {/* Home Airport Modal */}
      <Modal visible={showHomeAirportModal} animationType="slide" transparent>
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <Text style={styles.modalTitle}>Select Home Airport</Text>
              <TextInput style={styles.searchInput} placeholder="Search..." placeholderTextColor="#666" value={airportSearch} onChangeText={setAirportSearch} />
              <FlatList data={filteredAirports.slice(0, 15)} keyExtractor={item => item.iata} renderItem={({ item }) => (
                <TouchableOpacity style={styles.airportItem} onPress={() => setHomeAirport(item.iata)}>
                  <Text style={styles.airportCode}>{item.iata}</Text>
                  <Text style={styles.airportName}>{item.city}, {item.country}</Text>
                </TouchableOpacity>
              )} style={{maxHeight: 300}} />
            </View>
          </View>
        </TouchableWithoutFeedback>
      </Modal>

      {/* Aircraft Purchase Modal */}
      <Modal visible={showAircraftModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}><Text style={styles.modalTitle}>Purchase Aircraft</Text><TouchableOpacity onPress={() => setShowAircraftModal(false)}><Ionicons name="close" size={24} color="#FFF" /></TouchableOpacity></View>
              {selectedAircraft && (
                <>
                  <Text style={styles.selectedName}>{selectedAircraft.brand} {selectedAircraft.model}</Text>
                  <Text style={styles.selectedPrice}>{formatCurrency(selectedAircraft.price)}</Text>
                  <TextInput style={styles.input} placeholder="Aircraft Name (e.g. N12345)" placeholderTextColor="#666" value={aircraftName} onChangeText={setAircraftName} />
                  <TouchableOpacity style={styles.checkboxRow} onPress={() => setUseLoan(!useLoan)}>
                    <Ionicons name={useLoan ? 'checkbox' : 'square-outline'} size={22} color="#4A90E2" />
                    <Text style={styles.checkboxLabel}>Finance with loan (7% APR)</Text>
                  </TouchableOpacity>
                  {useLoan && (
                    <>
                      <TextInput style={styles.input} placeholder="Loan Amount" placeholderTextColor="#666" value={loanAmount} onChangeText={setLoanAmount} keyboardType="numeric" />
                      <TextInput style={styles.input} placeholder="Term (months)" placeholderTextColor="#666" value={loanTerm} onChangeText={setLoanTerm} keyboardType="numeric" />
                    </>
                  )}
                  <TouchableOpacity style={styles.primaryBtn} onPress={purchaseAircraft}><Text style={styles.primaryBtnText}>Purchase</Text></TouchableOpacity>
                </>
              )}
            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>

      {/* Route Modal - Destination Selection */}
      <Modal visible={showRouteModal} animationType="slide" transparent>
        <TouchableWithoutFeedback onPress={Keyboard.dismiss}>
          <View style={styles.modalOverlay}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}><Text style={styles.modalTitle}>Select Destination</Text><TouchableOpacity onPress={() => setShowRouteModal(false)}><Ionicons name="close" size={24} color="#FFF" /></TouchableOpacity></View>
              <TextInput style={styles.searchInput} placeholder="Search..." placeholderTextColor="#666" value={airportSearch} onChangeText={setAirportSearch} />
              <FlatList data={filteredAirports.filter(a => a.iata !== selectedOrigin?.iata).slice(0, 10)} keyExtractor={item => item.iata} renderItem={({ item }) => (
                <TouchableOpacity style={[styles.airportItem, selectedDestination?.iata === item.iata && {backgroundColor:'#4A90E2'}]} onPress={() => { setSelectedDestination(item); setShowRouteModal(false); setAirportSearch(''); }}>
                  <Text style={[styles.airportCode, selectedDestination?.iata === item.iata && {color:'#FFF'}]}>{item.iata}</Text>
                  <Text style={styles.airportName}>{item.city}, {item.country}</Text>
                </TouchableOpacity>
              )} style={{maxHeight: 250}} />
            </View>
          </View>
        </TouchableWithoutFeedback>
      </Modal>

      {/* Loan Modal */}
      <Modal visible={showLoanModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}><Text style={styles.modalTitle}>New Loan</Text><TouchableOpacity onPress={() => setShowLoanModal(false)}><Ionicons name="close" size={24} color="#FFF" /></TouchableOpacity></View>
              <Text style={styles.loanInfo}>7% APR | Auto-pay on 1st of month</Text>
              <TextInput style={styles.input} placeholder="Loan Amount" placeholderTextColor="#666" value={loanAmount} onChangeText={setLoanAmount} keyboardType="numeric" />
              <TextInput style={styles.input} placeholder="Term (months)" placeholderTextColor="#666" value={loanTerm} onChangeText={setLoanTerm} keyboardType="numeric" />
              <TouchableOpacity style={styles.primaryBtn} onPress={() => createLoan(parseInt(loanAmount) || 0, parseInt(loanTerm) || 60)}><Text style={styles.primaryBtnText}>Apply</Text></TouchableOpacity>
            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>

      {/* Loan Payment Modal */}
      <Modal visible={showLoanPaymentModal} animationType="slide" transparent>
        <View style={styles.modalOverlay}>
          <KeyboardAvoidingView behavior={Platform.OS === 'ios' ? 'padding' : 'height'}>
            <View style={styles.modalContent}>
              <View style={styles.modalHeader}><Text style={styles.modalTitle}>Make Payment</Text><TouchableOpacity onPress={() => setShowLoanPaymentModal(false)}><Ionicons name="close" size={24} color="#FFF" /></TouchableOpacity></View>
              {selectedLoan && <Text style={styles.loanInfo}>Remaining: {formatCurrency(selectedLoan.remaining)}</Text>}
              <TextInput style={styles.input} placeholder="Payment Amount" placeholderTextColor="#666" value={paymentAmount} onChangeText={setPaymentAmount} keyboardType="numeric" />
              <TouchableOpacity style={styles.primaryBtn} onPress={payLoan}><Text style={styles.primaryBtnText}>Pay</Text></TouchableOpacity>
            </View>
          </KeyboardAvoidingView>
        </View>
      </Modal>

      {/* Sell Aircraft Modal */}
      <Modal visible={showSellModal} animationType="fade" transparent>
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Sell Aircraft?</Text>
            {aircraftToSell && (
              <>
                <Text style={styles.sellInfo}>{aircraftToSell.name}</Text>
                <Text style={styles.sellPrice}>Sell for: {formatCurrency((aircraftToSell.details?.price || 0) * 0.7)}</Text>
              </>
            )}
            <View style={styles.sellButtons}>
              <TouchableOpacity style={styles.cancelBtn} onPress={() => setShowSellModal(false)}><Text style={styles.cancelBtnText}>Cancel</Text></TouchableOpacity>
              <TouchableOpacity style={styles.confirmBtn} onPress={sellAircraft}><Text style={styles.confirmBtnText}>Sell</Text></TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0A0A0A' },
  loadingContainer: { flex: 1, justifyContent: 'center', alignItems: 'center', backgroundColor: '#0A0A0A' },
  loadingText: { color: '#FFF', marginTop: 16 },
  content: { flex: 1 },
  tabContent: { flex: 1, padding: 12 },
  header: { marginBottom: 16 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#FFF' },
  headerDate: { fontSize: 12, color: '#888', marginTop: 2 },
  balanceCard: { backgroundColor: '#1A1A1A', borderRadius: 12, padding: 16, marginBottom: 12 },
  balanceLabel: { fontSize: 12, color: '#888' },
  balanceAmount: { fontSize: 28, fontWeight: 'bold', color: '#4A90E2', marginTop: 4 },
  statsRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  statCard: { flex: 1, backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, alignItems: 'center', marginHorizontal: 3 },
  statValue: { fontSize: 18, fontWeight: 'bold', color: '#FFF', marginTop: 4 },
  statLabel: { fontSize: 10, color: '#888', marginTop: 2 },
  homeAirportCard: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 12 },
  homeAirportText: { color: '#FFF', marginLeft: 8, fontSize: 14 },
  actionButton: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#4A90E2', borderRadius: 10, padding: 14, marginBottom: 16 },
  actionButtonText: { color: '#FFF', fontWeight: '600', marginLeft: 8 },
  section: { marginTop: 8 },
  sectionHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: 'bold', color: '#FFF', marginBottom: 8 },
  addBtn: { backgroundColor: '#4A90E2', borderRadius: 16, width: 32, height: 32, justifyContent: 'center', alignItems: 'center' },
  flightCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  flightHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  flightRoute: { fontSize: 14, fontWeight: 'bold', color: '#FFF' },
  flightProgress: { fontSize: 14, color: '#4A90E2', fontWeight: '600' },
  progressBar: { height: 3, backgroundColor: '#333', borderRadius: 2, marginTop: 8, overflow: 'hidden' },
  progressFill: { height: '100%', backgroundColor: '#4A90E2', borderRadius: 2 },
  flightInfo: { color: '#888', marginTop: 6, fontSize: 12 },
  tabBar: { backgroundColor: '#1A1A1A', borderTopWidth: 1, borderTopColor: '#333', paddingBottom: Platform.OS === 'ios' ? 20 : 8 },
  tabBarContent: { paddingHorizontal: 8 },
  tabItem: { alignItems: 'center', paddingVertical: 12, paddingHorizontal: 20, minWidth: 70 },
  tabItemActive: { borderTopWidth: 2, borderTopColor: '#4A90E2' },
  tabLabel: { fontSize: 12, color: '#666', marginTop: 4 },
  tabLabelActive: { color: '#4A90E2' },
  mapContainer: { flex: 1 },
  map: { flex: 1 },
  mapPanel: { backgroundColor: '#1A1A1A', borderTopLeftRadius: 12, borderTopRightRadius: 12, padding: 12 },
  mapPanelEmpty: { padding: 16, alignItems: 'center' },
  mapPanelEmptyText: { color: '#666' },
  mapAircraftList: { marginBottom: 8 },
  mapAircraftItem: { backgroundColor: '#0A0A0A', borderRadius: 8, padding: 10, marginRight: 8, minWidth: 70, alignItems: 'center' },
  mapAircraftItemSelected: { backgroundColor: '#4A90E2' },
  mapAircraftName: { color: '#FFF', fontWeight: '600', fontSize: 11 },
  mapAircraftLoc: { color: '#888', fontSize: 9, marginTop: 2 },
  mapRouteInfo: { backgroundColor: '#0A0A0A', borderRadius: 8, padding: 10 },
  mapRouteRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 },
  mapLabel: { color: '#888', fontSize: 11 },
  mapInstruction: { color: '#4A90E2', fontSize: 11, marginBottom: 8, textAlign: 'center' },
  destSelectBtn: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#333', borderRadius: 6, paddingHorizontal: 10, paddingVertical: 6 },
  destSelectText: { color: '#FFF', fontSize: 11, marginRight: 4 },
  mapTypeRow: { flexDirection: 'row', marginBottom: 8 },
  mapTypeBtn: { flex: 1, backgroundColor: '#333', borderRadius: 6, padding: 8, marginRight: 6, alignItems: 'center' },
  mapTypeBtnActive: { backgroundColor: '#4A90E2' },
  mapTypeText: { color: '#888', fontSize: 11 },
  mapPriceRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  mapPriceInput: { flex: 1, backgroundColor: '#333', borderRadius: 6, padding: 8, color: '#FFF', fontSize: 12, marginRight: 8 },
  mapProfitText: { fontSize: 12, fontWeight: '600' },
  mapStartBtn: { flexDirection: 'row', backgroundColor: '#4CAF50', borderRadius: 8, padding: 10, alignItems: 'center', justifyContent: 'center' },
  mapStartText: { color: '#FFF', fontWeight: '600', marginLeft: 6, fontSize: 12 },
  weatherWidget: { backgroundColor: '#1A2A1A', borderRadius: 6, padding: 8, marginBottom: 8, borderLeftWidth: 3, borderLeftColor: '#4CAF50' },
  weatherWidgetHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 4 },
  weatherWidgetText: { color: '#FFF', fontSize: 11, marginLeft: 6, textTransform: 'capitalize' },
  weatherWidgetDetails: { flexDirection: 'row', flexWrap: 'wrap' },
  weatherWidgetDetail: { color: '#888', fontSize: 10, marginRight: 10 },
  fuelWidget: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#2A1A1A', borderRadius: 6, padding: 6, marginBottom: 8, borderLeftWidth: 3, borderLeftColor: '#FF9800' },
  fuelWidgetText: { color: '#888', fontSize: 10, marginLeft: 6 },
  aircraftCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  aircraftHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  aircraftName: { fontSize: 14, fontWeight: 'bold', color: '#FFF' },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 },
  statusText: { color: '#FFF', fontSize: 10, fontWeight: '600', textTransform: 'uppercase' },
  aircraftModel: { color: '#888', marginTop: 2, fontSize: 12 },
  aircraftStats: { flexDirection: 'row', marginTop: 8 },
  aircraftStatText: { color: '#888', fontSize: 11, marginRight: 12 },
  sellBtn: { backgroundColor: '#F44336', borderRadius: 6, padding: 8, marginTop: 8, alignItems: 'center' },
  sellBtnText: { color: '#FFF', fontSize: 12, fontWeight: '600' },
  brandFilter: { marginBottom: 12 },
  brandChip: { backgroundColor: '#1A1A1A', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 16, marginRight: 6 },
  brandChipActive: { backgroundColor: '#4A90E2' },
  brandChipText: { color: '#888', fontSize: 12 },
  brandTitle: { fontSize: 14, fontWeight: 'bold', color: '#4A90E2', marginTop: 12, marginBottom: 8 },
  storeCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  storeCardHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  storeCardTitle: { fontSize: 13, fontWeight: 'bold', color: '#FFF' },
  storeCardPrice: { fontSize: 13, color: '#4CAF50', fontWeight: '600' },
  storeCardStats: { color: '#888', fontSize: 11, marginTop: 6 },
  routeCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  routeHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  routeTitle: { fontSize: 14, fontWeight: 'bold', color: '#FFF' },
  cancelFlightBtn: { marginLeft: 8, padding: 4 },
  routeStats: { flexDirection: 'row', marginTop: 8 },
  routeStat: { color: '#888', fontSize: 11, marginRight: 12 },
  routeFinancials: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: '#333' },
  alertBanner: { flexDirection: 'row', alignItems: 'center', padding: 6, borderRadius: 4, marginVertical: 4, borderWidth: 1 },
  weatherNote: { color: '#888', fontSize: 11, marginBottom: 12 },
  weatherCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  weatherHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  weatherAirport: { fontSize: 14, fontWeight: 'bold', color: '#FFF' },
  weatherBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 8 },
  weatherBadgeText: { color: '#FFF', fontSize: 10, fontWeight: '600', textTransform: 'uppercase' },
  weatherDetails: { flexDirection: 'row', flexWrap: 'wrap', marginTop: 8 },
  weatherDetail: { color: '#888', fontSize: 11, marginRight: 12, marginBottom: 4 },
  financeCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  financeLabel: { color: '#888', fontSize: 12 },
  financeValue: { fontSize: 20, fontWeight: 'bold', marginTop: 4 },
  loanCard: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 12, marginBottom: 8 },
  loanHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  loanAmount: { fontSize: 16, fontWeight: 'bold', color: '#FFF' },
  loanRate: { color: '#FF9800', fontWeight: '600', fontSize: 12 },
  loanDetail: { color: '#888', fontSize: 11, marginTop: 4 },
  loanInfo: { color: '#888', marginBottom: 12, textAlign: 'center', fontSize: 12 },
  payBtn: { backgroundColor: '#4A90E2', borderRadius: 6, padding: 8, marginTop: 8, alignItems: 'center' },
  payBtnText: { color: '#FFF', fontSize: 12, fontWeight: '600' },
  settingsItem: { flexDirection: 'row', alignItems: 'center', backgroundColor: '#1A1A1A', borderRadius: 10, padding: 14, marginBottom: 8 },
  settingsText: { color: '#FFF', marginLeft: 12, fontSize: 14 },
  settingsInfo: { backgroundColor: '#1A1A1A', borderRadius: 10, padding: 14, marginTop: 16 },
  settingsInfoText: { color: '#888', fontSize: 12, marginBottom: 4 },
  themeToggle: { width: 50, height: 26, borderRadius: 13, padding: 2, justifyContent: 'center' },
  themeToggleBtn: { width: 22, height: 22, borderRadius: 11, alignItems: 'center', justifyContent: 'center' },
  emptyState: { alignItems: 'center', padding: 24 },
  emptyText: { fontSize: 14, color: '#888', marginTop: 12 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#1A1A1A', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20, maxHeight: '75%' },
  modalHeader: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 },
  modalTitle: { fontSize: 18, fontWeight: 'bold', color: '#FFF' },
  searchInput: { backgroundColor: '#0A0A0A', borderRadius: 8, padding: 10, color: '#FFF', marginBottom: 10, fontSize: 14 },
  input: { backgroundColor: '#0A0A0A', borderRadius: 8, padding: 12, color: '#FFF', marginBottom: 12, fontSize: 14 },
  airportItem: { flexDirection: 'row', alignItems: 'center', padding: 10, backgroundColor: '#0A0A0A', borderRadius: 6, marginBottom: 6 },
  airportCode: { fontSize: 14, fontWeight: 'bold', color: '#4A90E2', width: 45 },
  airportName: { color: '#FFF', fontSize: 12, flex: 1 },
  selectedName: { fontSize: 16, fontWeight: 'bold', color: '#FFF', textAlign: 'center' },
  selectedPrice: { fontSize: 20, color: '#4CAF50', fontWeight: 'bold', textAlign: 'center', marginBottom: 16 },
  checkboxRow: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  checkboxLabel: { color: '#FFF', marginLeft: 10, fontSize: 13 },
  primaryBtn: { backgroundColor: '#4A90E2', borderRadius: 10, padding: 14, alignItems: 'center', marginTop: 8 },
  primaryBtnText: { color: '#FFF', fontSize: 14, fontWeight: '600' },
  tutorialContent: { backgroundColor: '#1A1A1A', margin: 20, borderRadius: 16, padding: 20 },
  tutorialTitle: { fontSize: 18, fontWeight: 'bold', color: '#FFF', textAlign: 'center', marginBottom: 16 },
  tutorialItem: { flexDirection: 'row', alignItems: 'center', marginBottom: 12 },
  tutorialText: { color: '#FFF', marginLeft: 12, fontSize: 13, flex: 1 },
  tutorialBtn: { backgroundColor: '#4A90E2', borderRadius: 10, padding: 14, alignItems: 'center', marginTop: 8 },
  tutorialBtnText: { color: '#FFF', fontSize: 14, fontWeight: '600' },
  sellInfo: { fontSize: 16, color: '#FFF', textAlign: 'center', marginBottom: 8 },
  sellPrice: { fontSize: 20, color: '#4CAF50', fontWeight: 'bold', textAlign: 'center', marginBottom: 16 },
  sellButtons: { flexDirection: 'row', justifyContent: 'space-between' },
  cancelBtn: { flex: 1, backgroundColor: '#333', borderRadius: 10, padding: 14, alignItems: 'center', marginRight: 8 },
  cancelBtnText: { color: '#FFF', fontSize: 14 },
  confirmBtn: { flex: 1, backgroundColor: '#F44336', borderRadius: 10, padding: 14, alignItems: 'center', marginLeft: 8 },
  confirmBtnText: { color: '#FFF', fontSize: 14, fontWeight: '600' },
  
  // Difficulty selection styles
  difficultyContent: { backgroundColor: '#1A1A1A', margin: 16, borderRadius: 16, padding: 20, maxHeight: '90%' },
  difficultyTitle: { fontSize: 22, fontWeight: 'bold', color: '#FFF', textAlign: 'center', marginBottom: 20 },
  difficultyOptions: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 20 },
  difficultyCard: { flex: 1, backgroundColor: '#0A0A0A', borderRadius: 12, padding: 14, marginHorizontal: 4, alignItems: 'center', borderWidth: 2, borderColor: 'transparent' },
  difficultyCardSelected: { borderColor: '#4A90E2', backgroundColor: '#4A90E2' },
  difficultyName: { fontSize: 16, fontWeight: 'bold', color: '#FFF', marginTop: 8 },
  difficultyDesc: { fontSize: 10, color: '#888', marginTop: 4, textAlign: 'center' },
  difficultyAirportSection: { marginTop: 8 },
  difficultySubtitle: { fontSize: 14, fontWeight: '600', color: '#FFF', marginBottom: 10 },
  airportItemSelected: { backgroundColor: '#4A90E2' },
  startGameBtn: { backgroundColor: '#4CAF50', borderRadius: 12, padding: 16, alignItems: 'center', marginTop: 16 },
  startGameText: { color: '#FFF', fontSize: 16, fontWeight: 'bold' },
  
  // License training styles
  licenseCard: { backgroundColor: '#1A1A1A', borderRadius: 12, padding: 16, margin: 16 },
  licenseTitle: { fontSize: 18, fontWeight: 'bold', color: '#FFF', textAlign: 'center' },
  licenseDesc: { color: '#888', textAlign: 'center', marginTop: 8 },
  licenseBtn: { backgroundColor: '#4A90E2', borderRadius: 10, padding: 14, alignItems: 'center', marginTop: 16 },
  licenseBtnText: { color: '#FFF', fontSize: 14, fontWeight: '600' },
  licenseProgress: { alignItems: 'center', marginTop: 16 },
  licenseProgressText: { color: '#FF9800', fontSize: 16, fontWeight: 'bold' },
  difficultyBadge: { alignSelf: 'center', paddingHorizontal: 12, paddingVertical: 4, borderRadius: 12, marginBottom: 12 },
  difficultyBadgeText: { color: '#FFF', fontSize: 10, fontWeight: 'bold' },
  
  // Certification card styles
  sectionSubtitle: { color: '#888', fontSize: 12, marginBottom: 12 },
  certCard: { backgroundColor: '#1A1A1A', borderRadius: 12, padding: 14, marginBottom: 10, borderLeftWidth: 3, borderLeftColor: '#4A90E2' },
  certCardComplete: { borderLeftColor: '#4CAF50', opacity: 0.8 },
  certHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 8 },
  certInfo: { flex: 1, marginLeft: 10 },
  certName: { color: '#FFF', fontSize: 14, fontWeight: '600' },
  certForm: { color: '#666', fontSize: 10 },
  certCost: { color: '#FF9800', fontSize: 14, fontWeight: 'bold' },
  certDesc: { color: '#888', fontSize: 11, marginBottom: 4 },
  certUnlocks: { color: '#4A90E2', fontSize: 10, marginBottom: 4 },
  certPrereqs: { color: '#F44336', fontSize: 10, fontStyle: 'italic' },
  certActions: { marginTop: 8, alignItems: 'flex-start' },
  certTraining: { flexDirection: 'row', alignItems: 'center' },
  certTrainingText: { color: '#FF9800', fontSize: 12, marginLeft: 8, marginRight: 8 },
  certStartBtn: { backgroundColor: '#4A90E2', borderRadius: 6, paddingHorizontal: 14, paddingVertical: 8 },
  certCompleteBtn: { backgroundColor: '#4CAF50', borderRadius: 6, paddingHorizontal: 14, paddingVertical: 8 },
  certBtnText: { color: '#FFF', fontSize: 12, fontWeight: '600' },
  certLocked: { color: '#666', fontSize: 11, fontStyle: 'italic' },
  
  // Flight mode styles
  mapModeRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 },
  mapModeBtn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', backgroundColor: '#0A0A0A', borderRadius: 6, paddingVertical: 8, paddingHorizontal: 6, marginHorizontal: 2, borderWidth: 1, borderColor: '#333' },
  mapModeBtnActive: { backgroundColor: '#4A90E2', borderColor: '#4A90E2' },
  mapModeBtnLocked: { opacity: 0.5 },
  mapModeText: { color: '#888', fontSize: 11, marginLeft: 4, marginRight: 2 },
  mapModeHint: { color: '#666', fontSize: 9, textAlign: 'center', marginBottom: 6, fontStyle: 'italic' },
});
