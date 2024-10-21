import React ,{useEffect, useState}from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from 'primereact/button';
import { MenuPopup } from "./popup";
import Cookies from 'js-cookie';
import { fetchItems,deleteItem } from "./service/menuapi";
import { placeorder } from "./service/userapi";
import 'primereact/resources/themes/saga-blue/theme.css';  // You can choose any theme here
import './menu.css'
import {BasketPopup} from './popup'

export function Menu() {
  const [clickedbtnType, setclickedbtnType] = useState();
  const [role, setRole] = useState(Cookies.get("role"));
  const [visible, setVisible] = useState(false);
  const [basketVisible, setBasketVisible] = useState(false); // State for basket visibility
  const [items, setItems] = useState([{"name": "x"}]);
  const [deleted, setDeleted] = useState(false);
  const [basket, setBasket] = useState([]);

  useEffect(() => {
    const menu = async () => {
      const data = await fetchItems();
      setItems(data);
    };
    if (!visible) {
      setDeleted(false);
      menu();
    }
  }, [visible, deleted]);

  async function delete_itemCall(data) {
    let req = { "item_id": data.item_id };
    try {
      let response = await deleteItem(req);
      setDeleted(true); // Update deleted state
      alert(response.message);
    } catch (Error) {
      alert("Error Occurred");
    }
  }

  async function placeorderCall() {
    try {
      let response = await placeorder(basket);
      setBasket([]); // Clear the basket after placing the order
      alert(response.message);
    } catch (Error) {
      alert("Error Occurred");
    }
  }

  function addToBasket(item) {
    const existingItem = basket.find(i => i.item_id === item.item_id);
    if (existingItem) {
      existingItem.qty += 1; // Increment the quantity if item exists
    } else {
      basket.push({ ...item, qty: 1 }); // Add new item with quantity 1
    }
    setBasket([...basket]); // Update state with new basket
  }

  function updateItemQty(itemId, change) {
    const updatedBasket = basket.map(item => {
      if (item.item_id === itemId) {
        const newQty = item.qty + change;
        return { ...item, qty: Math.max(newQty, 0) }; // Prevent negative quantities
      }
      return item;
    }).filter(item => item.qty > 0); // Remove items with qty <= 0

    setBasket(updatedBasket); // Update basket state
  }

  function btnClick(functionality) {
    if (functionality === "Add") {
      functionality = {};
      functionality.label = "Add";
    } else {
      functionality.label = "Update";
    }
    setclickedbtnType(functionality);
    setVisible(true);
  }

  return (
    <div className="menu-container">
      <div className="header">
        <h1>Hotel Menu</h1>
        {role !== "user" && (
          <div className="button-group">
            <Button onClick={() => btnClick("Add")} icon="pi-plus" label="Add Item" className="hotel-button" />
          </div>
        )}
        {role === "user" && (
          <div className="button-group">
            <Button onClick={placeorderCall} icon="pi-plus" label="Place Order" className="hotel-button" />
            <Button onClick={() => setBasketVisible(true)} className="hotel-button">View Basket</Button>
          </div>
        )}
      </div>
      <DataTable value={items} className="hotel-menu-table">
        <Column field="name" header="Dish Name"></Column>
        <Column field="description" header="Description"></Column>
        <Column field="price" header="Price" body={(rowData) => `$${rowData.price}`}></Column>
        <Column field="qty" header="Quantity" body={(data) => {
          const itemInBasket = basket.find(i => i.item_id === data.item_id);
          return itemInBasket ? (
            <div className="qty-controls">
              <Button 
                icon="pi pi-minus" 
                onClick={() => updateItemQty(data.item_id, -1)} 
                disabled={!itemInBasket || itemInBasket.qty <= 0}
                className="qty-button" 
              />
              <span>{itemInBasket.qty}</span>
              <Button 
                icon="pi pi-plus" 
                onClick={() => updateItemQty(data.item_id, 1)} 
                className="qty-button" 
              />
            </div>
          ) : (
            0 // Show 0 if not in basket
          );
        }}></Column>
        <Column
          header=""
          body={(data) => (
            <div className="button-group">
              {role !== "user" ? (
                <>
                  <Button onClick={() => btnClick(data)} className="hotel-button">Edit</Button>
                  <Button onClick={() => delete_itemCall(data)} className="hotel-button">Delete</Button>
                </>
              ) : (
                <Button onClick={() => addToBasket(data)} className="hotel-button">Add To Basket</Button>
              )}
            </div>
          )}
        />
      </DataTable>
      {visible && <MenuPopup visible={visible} onHide={() => setVisible(false)} type={clickedbtnType} />}
      <BasketPopup visible={basketVisible} onHide={() => setBasketVisible(false)} basket={basket} />
    </div>
  );
}