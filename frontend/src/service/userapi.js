import axios from 'axios';
import Cookies from 'js-cookie';
const API_URL = 'http://127.0.0.1:5000/user';



export const signup = async (loginData) => {
    try {
        const response = await axios.post(`${API_URL}/signup`, loginData);
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error signing Up:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Signing UP Failed');
        }
    }
};

export const signin = async (loginData) => {
    try {
        const response = await axios.post(`${API_URL}/signin`, loginData);
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error signing Up:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Signing In failed');
        }
    }
};


export const bookslot = async (slotdata) => {
    let token = Cookies.get("authToken")
    try {
        const response = await axios.post(`${API_URL}/bookslot`, slotdata,
            {
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
                }
            }
        );
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error signing Up:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Signing In failed');
        }
    }
};

export const placeorder = async (orderdata) => {
    let token = Cookies.get("authToken")
    try {
        const response = await axios.post(`${API_URL}/placeorder`, orderdata,
            {
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
                }
            }
        );
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error signing Up:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Signing In failed');
        }
    }
};
