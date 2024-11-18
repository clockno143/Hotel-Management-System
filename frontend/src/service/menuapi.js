import axios from 'axios';
import Cookies from 'js-cookie';


const API_URL = 'http://127.0.0.1:5000/menu';

export const fetchItems = async () => {
    let token = Cookies.get("authToken")
    
    const response = await axios.get(`${API_URL}`,{
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
        }
    });
    console.log(response)
    return response.data;
};

export const insertItem = async (itemData) => {
    let token = Cookies.get("authToken")

    try {
        const response = await axios.post(`${API_URL}/add`, itemData,{
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
            }
        });
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
    let token = Cookies.get("authToken")

    try {
        const response = await axios.post(`${API_URL}/update`, itemData,{
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
            }
        });
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
    let token = Cookies.get("authToken")

    try {
        const response = await axios.post(`${API_URL}/delete`, itemData,{
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}` // Passing JWT token in the Authorization header
            }
        });
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