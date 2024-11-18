import axios from 'axios';
import Cookies from 'js-cookie';

const API_URL = 'http://127.0.0.1:5000/slot';

export const upsertSlot = async (slotData) => {
    let token = Cookies.get("authToken")
    try {
        const response = await axios.post(`${API_URL}/upsert`, slotData,
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
        console.error('Error updating item:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Failed to update item');
        }
    }
};

export const fetchSlots = async () => {
    let token = Cookies.get("authToken")
    const response = await axios.get(`${API_URL}`,
        {
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
            }
        }
    );
    console.log(response)
    return response.data;
};