import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/slot';

export const upsertSlot = async (slotData) => {
    try {
        const response = await axios.post(`${API_URL}/upsert`, slotData);
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
    const response = await axios.get(`${API_URL}`);
    console.log(response)
    return response.data;
};