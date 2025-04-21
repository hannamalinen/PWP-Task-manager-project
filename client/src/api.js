import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:5000/api", // Replace with your API base URL
});

export default API;