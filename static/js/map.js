// Initialize map
mapManager.initMap('map-container');

// Add pharmacies with medicine info
mapManager.addPharmacies(pharmacies, medicineInfoMap);

// Get user location
mapManager.getUserLocation();

// Listen to events
window.addEventListener('map:locationFound', (event) => {
    console.log('User location:', event.detail);
});

window.addEventListener('map:directionsRequested', (event) => {
    console.log('Directions from:', event.detail.from, 'to:', event.detail.to);
});