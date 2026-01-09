const API_URL = import.meta.env.VITE_API_URL

export const api = {
    // this is how you add a method to an object: method: ...
    async get (endpoint) {
        const token = localStorage.getItem("token")
        const headers = {
            "Content-Type": 'application/json'
        }
        if (token) {
            headers["Authorization"] = `Bearer ${token}`
        }
        const response = await fetch(API_URL + endpoint, {headers: headers});
        if (!response.ok) {
             throw new Error("Network error")
        }
        return response.json()
    },
    async post(endpoint, data) {
        const token = localStorage.getItem("token")
        const headers = {
            "Content-Type": "application/json"
        }
        if (token) {
            headers["Authorization"] = `Bearer ${token}`
        }
        const response = await fetch(API_URL + endpoint, {
            method: "POST",
            headers: headers,
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            throw new Error(await response.text())
        }
        return response.json()
    }
}