import axios from 'axios';

const API_URL = 'http://127.0.0.1:5000/menu';

export const fetchItems = async () => {
    const response = await axios.get(`${API_URL}`);
    console.log(response)
    return response.data;
};

export const insertItem = async (itemData) => {
    try {
        const response = await axios.post(`${API_URL}/add`, itemData);
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error adding item:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Failed to add item');
        }
    }
};

export const updateItem = async (itemData) => {
    try {
        const response = await axios.post(`${API_URL}/update`, itemData);
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

export const deleteItem = async (itemData) => {
    try {
        const response = await axios.post(`${API_URL}/delete`, itemData);
        console.log(response);
        return response.data;
    } catch (error) {
        console.error('Error Deleting item:', error);
        if (error.response) {
            throw new Error(error.response.data.error);
        } else {
            throw new Error('Failed to Delete item');
        }
    }
};