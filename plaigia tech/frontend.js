/**
 * PlagiaTech Frontend Integration
 * 
 * This script integrates the frontend with the backend API.
 */

// API base URL - change this to match your deployment
const API_BASE_URL = 'http://localhost:8000/api';

// DOM elements
const inputText = document.getElementById('inputText');
const plagiarismReport = document.getElementById('plagiarismReport');
const rephrasedContent = document.getElementById('rephrasedContent');
const loadingIndicator = document.getElementById('loading');
const errorMessage = document.getElementById('error');

// Authentication state
let authToken = localStorage.getItem('authToken');
let isAuthenticated = !!authToken;

/**
 * Check text for plagiarism
 */
async function checkPlagiarism() {
    if (!inputText.value.trim()) {
        showError('Please enter some text to check for plagiarism.');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/check-plagiarism`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(isAuthenticated && { 'Authorization': `Bearer ${authToken}` })
            },
            body: JSON.stringify({ text: inputText.value })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to check plagiarism');
        }

        const result = await response.json();
        
        // Format the plagiarism report
        const percentage = result.percentage;
        const sources = result.sources;
        
        let reportHtml = `<strong>${percentage}%</strong> similarity detected.`;
        
        if (sources && sources.length > 0) {
            reportHtml += '<br><br>Sources:<ul>';
            sources.forEach(source => {
                reportHtml += `<li><a href="${source}" target="_blank">${source}</a></li>`;
            });
            reportHtml += '</ul>';
        }
        
        plagiarismReport.innerHTML = reportHtml;
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Rephrase text using AI
 */
async function rephraseText() {
    if (!inputText.value.trim()) {
        showError('Please enter some text to rephrase.');
        return;
    }

    showLoading();
    hideError();

    try {
        const response = await fetch(`${API_BASE_URL}/rephrase`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(isAuthenticated && { 'Authorization': `Bearer ${authToken}` })
            },
            body: JSON.stringify({ text: inputText.value })
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to rephrase text');
        }

        const result = await response.json();
        rephrasedContent.innerText = result.rephrased;
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Copy rephrased text to clipboard
 */
function copyText() {
    const text = rephrasedContent.innerText;
    if (!text || text.includes('Rephrased text will appear here')) {
        showError('No rephrased text to copy.');
        return;
    }

    navigator.clipboard.writeText(text).then(() => {
        // Show a temporary success message
        const originalText = rephrasedContent.innerText;
        rephrasedContent.innerText = 'Text copied to clipboard!';
        setTimeout(() => {
            rephrasedContent.innerText = originalText;
        }, 1500);
    }).catch(err => {
        showError('Failed to copy text: ' + err);
    });
}

/**
 * Show loading indicator
 */
function showLoading() {
    loadingIndicator.style.display = 'block';
}

/**
 * Hide loading indicator
 */
function hideLoading() {
    loadingIndicator.style.display = 'none';
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.innerText = message;
    errorMessage.style.display = 'block';
}

/**
 * Hide error message
 */
function hideError() {
    errorMessage.style.display = 'none';
}

/**
 * Login form handler
 */
async function login(event) {
    if (event) event.preventDefault();
    
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    if (!username || !password) {
        showError('Please enter both username and password.');
        return;
    }
    
    showLoading();
    hideError();
    
    try {
        const formData = new FormData();
        formData.append('username', username);
        formData.append('password', password);
        
        const response = await fetch(`${API_BASE_URL}/token`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Login failed');
        }
        
        const data = await response.json();
        authToken = data.access_token;
        localStorage.setItem('authToken', authToken);
        isAuthenticated = true;
        
        // Update UI to show logged in state
        document.getElementById('loginSection').style.display = 'none';
        document.getElementById('userSection').style.display = 'block';
        document.getElementById('userWelcome').innerText = `Welcome, ${username}!`;
        
        // Fetch user stats
        fetchUserStats();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Register form handler
 */
async function register(event) {
    if (event) event.preventDefault();
    
    const username = document.getElementById('registerUsername').value;
    const email = document.getElementById('registerEmail').value;
    const password = document.getElementById('registerPassword').value;
    
    if (!username || !email || !password) {
        showError('Please fill in all registration fields.');
        return;
    }
    
    showLoading();
    hideError();
    
    try {
        const response = await fetch(`${API_BASE_URL}/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username,
                email,
                password
            })
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Registration failed');
        }
        
        // Show success message and switch to login
        document.getElementById('registerForm').reset();
        alert('Registration successful! Please log in.');
        
        // Switch to login tab
        document.getElementById('loginTab').click();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Fetch user statistics
 */
async function fetchUserStats() {
    if (!isAuthenticated) return;
    
    try {
        const response = await fetch(`${API_BASE_URL}/usage`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            if (response.status === 401) {
                // Token expired, log out
                logout();
                return;
            }
            throw new Error('Failed to fetch user stats');
        }
        
        const data = await response.json();
        
        // Update UI with user stats
        document.getElementById('usageCount').innerText = data.total_checks;
        document.getElementById('remainingChecks').innerText = 
            data.is_premium ? 'Unlimited' : data.remaining_free_checks;
        document.getElementById('premiumStatus').innerText = 
            data.is_premium ? 'Premium' : 'Free';
        
        // Show/hide upgrade button
        document.getElementById('upgradeButton').style.display = 
            data.is_premium ? 'none' : 'inline-block';
    } catch (error) {
        console.error('Error fetching user stats:', error);
    }
}

/**
 * Upgrade to premium
 */
async function upgradeToPremium() {
    if (!isAuthenticated) {
        showError('Please log in to upgrade.');
        return;
    }
    
    showLoading();
    hideError();
    
    try {
        // In a real app, this would redirect to a payment processor
        // For demo purposes, we'll just call the upgrade endpoint directly
        const response = await fetch(`${API_BASE_URL}/premium`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Upgrade failed');
        }
        
        alert('Upgraded to premium successfully!');
        
        // Refresh user stats
        fetchUserStats();
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Logout user
 */
function logout() {
    localStorage.removeItem('authToken');
    authToken = null;
    isAuthenticated = false;
    
    // Update UI to show logged out state
    document.getElementById('loginSection').style.display = 'block';
    document.getElementById('userSection').style.display = 'none';
}

/**
 * Initialize the application
 */
function initApp() {
    // Check if user is already logged in
    if (isAuthenticated) {
        // Validate token and fetch user info
        fetch(`${API_BASE_URL}/me`, {
            headers: {
                'Authorization': `Bearer ${authToken}`
            }
        }).then(response => {
            if (!response.ok) {
                // Token invalid or expired
                logout();
                return null;
            }
            return response.json();
        }).then(user => {
            if (user) {
                // Update UI with user info
                document.getElementById('loginSection').style.display = 'none';
                document.getElementById('userSection').style.display = 'block';
                document.getElementById('userWelcome').innerText = `Welcome, ${user.username}!`;
                
                // Fetch user stats
                fetchUserStats();
            }
        }).catch(error => {
            console.error('Error validating token:', error);
            logout();
        });
    }
    
    // Add event listeners for login/register forms if they exist
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', login);
    }
    
    const registerForm = document.getElementById('registerForm');
    if (registerForm) {
        registerForm.addEventListener('submit', register);
    }
    
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }
    
    const upgradeButton = document.getElementById('upgradeButton');
    if (upgradeButton) {
        upgradeButton.addEventListener('click', upgradeToPremium);
    }
}

// Initialize the app when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', initApp);
