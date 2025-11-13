// Geolocation functionality for finding nearby parking lots

class GeolocationService {
  constructor() {
    this.userLocation = null;
  }

  /**
   * Request user's location with permission
   */
  async getUserLocation() {
    return new Promise((resolve, reject) => {
      if (!navigator.geolocation) {
        reject(new Error('Geolocation is not supported by your browser'));
        return;
      }

      navigator.geolocation.getCurrentPosition(
        (position) => {
          this.userLocation = {
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          resolve(this.userLocation);
        },
        (error) => {
          let errorMessage = 'Unable to retrieve location';
          switch (error.code) {
            case error.PERMISSION_DENIED:
              errorMessage = 'Location permission denied. Please enable location access in your browser settings.';
              break;
            case error.POSITION_UNAVAILABLE:
              errorMessage = 'Location information is unavailable.';
              break;
            case error.TIMEOUT:
              errorMessage = 'Location request timed out.';
              break;
          }
          reject(new Error(errorMessage));
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 0
        }
      );
    });
  }

  /**
   * Fetch nearby parking lots from the API
   */
  async getNearbyParking(latitude, longitude, radius = 10) {
    try {
      const response = await fetch(
        `/user/api/nearby-parking?lat=${latitude}&lon=${longitude}&radius=${radius}`
      );

      if (!response.ok) {
        throw new Error('Failed to fetch nearby parking');
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error fetching nearby parking:', error);
      throw error;
    }
  }

  /**
   * Display loading state
   */
  showLoading(containerId) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = `
        <div class="text-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-3 text-secondary">Finding nearby parking...</p>
        </div>
      `;
    }
  }

  /**
   * Display error message
   */
  showError(containerId, message) {
    const container = document.getElementById(containerId);
    if (container) {
      container.innerHTML = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          <strong>Error:</strong> ${message}
          <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
      `;
    }
  }

  /**
   * Display nearby parking lots
   */
  displayNearbyParking(containerId, parkingData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (parkingData.length === 0) {
      container.innerHTML = `
        <div class="alert alert-info">
          <h5>No nearby parking found</h5>
          <p>Try increasing the search radius or browse all available parking lots.</p>
        </div>
      `;
      return;
    }

    let html = '<div class="row g-4">';

    parkingData.forEach(item => {
      const lot = item.lot;
      const distance = item.distance;
      const availableSpots = item.available_spots || 0;

      html += `
        <div class="col-md-6 col-lg-4">
          <div class="card h-100 fade-in">
            <div class="card-body">
              <div class="d-flex justify-content-between align-items-start mb-3">
                <h5 class="card-title mb-0">${lot.location}</h5>
                <span class="badge bg-primary">${distance} km</span>
              </div>
              <p class="card-text text-secondary mb-2">
                <i class="bi bi-geo-alt"></i> ${lot.address}, ${lot.pincode}
              </p>
              <div class="d-flex justify-content-between align-items-center mb-3">
                <span class="text-success fw-bold">₹${lot.price}/hour</span>
                <span class="badge ${availableSpots > 0 ? 'bg-success' : 'bg-danger'}">
                  ${availableSpots} spots available
                </span>
              </div>
              <a href="/book/${lot.id}" class="btn btn-primary w-100 ${availableSpots === 0 ? 'disabled' : ''}">
                ${availableSpots > 0 ? 'Book Now' : 'Full'}
              </a>
            </div>
          </div>
        </div>
      `;
    });

    html += '</div>';
    container.innerHTML = html;
  }

  /**
   * Main function to find and display nearby parking
   */
  async findNearbyParking(containerId, radius = 10) {
    try {
      // Show loading state
      this.showLoading(containerId);

      // Get user's location
      const location = await this.getUserLocation();

      // Fetch nearby parking
      const nearbyParking = await this.getNearbyParking(
        location.latitude,
        location.longitude,
        radius
      );

      // Display results
      this.displayNearbyParking(containerId, nearbyParking);

    } catch (error) {
      this.showError(containerId, error.message);
    }
  }
}

// Initialize geolocation service
const geoService = new GeolocationService();

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
  module.exports = GeolocationService;
}
