// Complex async function with potential issues
async function fetchUserData(userId) {
    try {
        const response = await fetch(`/api/users/${userId}`);
        const data = await response.json();
        
        // Potential bug: not checking response.ok
        return data;
    } catch (error) {
        console.log(error); // Should use proper error handling
        return null;
    }
}

// Memory leak potential
let cache = {};
function cacheData(key, value) {
    cache[key] = value; // Never clears old entries
}