/** This file configures the Axios instance used for making API requests.
 * It sets the base URL for the backend API and exports the configured instance. */

import axios from "axios";

/**
 * Axios instance configured for making API requests to the backend.
 */
const API = axios.create({
    baseURL: "http://127.0.0.1:5000/api", // Replace with your API base URL
});

export default API;