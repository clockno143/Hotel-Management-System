import React ,{useContext,useEffect,useState} from "react";
import { Sidebar } from "primereact/sidebar";
import { Column } from "primereact/column";
import 'primereact/resources/themes/saga-blue/theme.css';  // You can choose any theme here
import 'primeicons/primeicons.css';
import {clickedBtn} from './Slot'
import { Calendar } from 'primereact/calendar';
import { Dropdown } from 'primereact/dropdown';
import { InputNumber } from 'primereact/inputnumber';
import { InputText } from 'primereact/inputtext';
import { InputTextarea } from "primereact/inputtextarea";
import { Button } from "primereact/button";
import { insertItem,updateItem } from "./service/menuapi";
import { Dialog } from 'primereact/dialog';
import{upsertSlot}  from "./service/slotapi"
export function Popup ({visible,onHide}){
      const {data} = useContext(clickedBtn)
      const [date,setDate] = useState()
      const [time, setTime] = useState()
      const [noofSlots,setnoofSlots] = useState(0)
      const [timeSlots,settimeslots] = useState([{"label":"11:00",value:"11:00"},{"label":"12:00",value:"12:00"},{"label":"13:00",value:"13:00"},
        {"label":"14:00",value:"14:00"},{"label":"15:00",value:"15:00"},{"label":"17:00",value:"17:00"},{"label":"18:00",value:"18:00"},
        {"label":"19:00",value:"19:00"},{"label":"20:00",value:"20:00"  },
      ])
      /*useEffect(()=>{
        const setDates= ()=>{
            if (data.label == 'Edit'){
                let dates = Object.keys(data.data)
                setDate(dates)
                setnoofSlots()
                setTime()
            }
        }
      },[])*/
      useEffect(()=>{
            const setTimes= ()=>{
             
                if (data.label =='Edit' && date){
                    let utcDate = new Date((date?.toString()))?.toISOString()
                    let time = Object.keys(data.data[utcDate]||{})
                    time.map((t)=>{return {"label":t,"value":t}})
                    settimeslots(time)
                    setnoofSlots(0)
                }
            }
            setTimes()
      },[date])
      useEffect(()=>{
            const setnoofSlot =() =>{
                if (data.label =='Edit' && time){
                    let utcDate = new Date((date?.toString()))?.toISOString()
                    let slots = data.data[utcDate][time]
                    setnoofSlots(slots)
                }
            }
            setnoofSlot()
      },[time])
      return (
      
                <Sidebar visible={visible} onHide={onHide}>
                <h2>Select Date</h2>
                <div style={{display:"flex",flexDirection:"column",justifyContent:"space-between", height:"25%"}}>
                <Calendar value={date} onChange={(e) => {setDate(e.value)}} showIcon placeholder=" Select Date"/>
                    <Dropdown value={time} placeholder="Select Time" onChange={(e)=>setTime(e.value)} options={timeSlots} optionLabel="label"></Dropdown>
                <InputNumber value={noofSlots} onChange={(e)=>setnoofSlots(e.value)} placeholder="Enter No of Slots"></InputNumber>
                <Button onClick={() =>upsertSlotCall() }>{data.label}</Button>
                </div>
                </Sidebar>
          
      );
      async function  upsertSlotCall(){
        console.log(data)
        let req ={
        "hotel_id": 1,
        "date":date,
        "time":time,
        "noofslots": parseInt(noofSlots)}
        try{
        let response = await upsertSlot(req)
        onHide()
        alert(response.message)
        }catch   (Error){
        alert("Error Occured")
        }
    
    }
    



}


export function MenuPopup ({visible,onHide,type}){
    
    const [itemName,setItemName] = useState(type.name)
    const [discription,setDiscription] = useState(type.description)
    const [price,setPrice] = useState(type.price)
    const [itemid ,setitemid] = useState(type.item_id)
    
    

   
    
    return (
        
        <Sidebar visible={visible} onHide={onHide}>
        <h2>Item</h2>
        <div style={{display:"flex",flexDirection:"column", height:"30%"}}>
        <InputText placeholder="Enter Item Name" value={itemName} onChange={(e)=> setItemName(e.target.value)}></InputText>
        <InputNumber placeholder="Enter Price" value={price} onChange={(e) => setPrice(e.value)}></InputNumber>
        <InputTextarea placeholder="Enter Item Discription" value={discription} onChange={(e) => setDiscription(e.target.value)} rows={40} cols={30} />
        </div>
        <Button onClick={()=>handelClick(type.label)}>{type.label}</Button>

        </Sidebar>
  
);
function handelClick(type){
    if (type == 'Update'){
        updateItemCall()
    }else{
        addItem()
    }
    onHide()
}
    async function  addItem(){
        let req ={
        "hotel_id": 1,
        "name":itemName,
        "description":discription,
        price: parseInt(price),}
        try{
        await insertItem(req)
        alert("Item Added Successfully")
        }catch   (Error){
        alert("Error Occured")
        }
    
  }

  async function  updateItemCall(){
    let req ={
    "hotel_id": 1,
    "name":itemName,
    "description":discription,
    price: parseInt(price),
    "item_id":itemid}
    try{
    let response = await updateItem(req)
    alert(response.message)
    }catch   (Error){
    alert("Error Occured")
    }

}



}


export const BasketPopup = ({ visible, onHide, basket }) => {
    const totalAmount = basket.reduce((acc, item) => acc + item.price * item.qty, 0).toFixed(2);
  
    return (
      <Dialog header="Your Basket" visible={visible} onHide={onHide} style={{ width: '50vw' }} modal>
        <div className="basket-container">
          {basket.length === 0 ? (
            <div className="empty-basket">Your basket is empty!</div>
          ) : (
            <>
              <table className="basket-table">
                <thead>
                  <tr>
                    <th>Name</th>
                    <th>Description</th>
                    <th>Quantity</th>
                    <th>Price</th>
                  </tr>
                </thead>
                <tbody>
                  {basket.map((item) => (
                    <tr key={item.item_id}>
                      <td>{item.name}</td>
                      <td>{item.description}</td>
                      <td>{item.qty}</td>
                      <td>${(item.price * item.qty).toFixed(2)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="basket-total">
                <strong>Total: ${totalAmount}</strong>
              </div>
              <div className="basket-actions">
                <Button label="Close" icon="pi pi-times" onClick={onHide} className="p-button-secondary" />
              </div>
            </>
          )}
        </div>
      </Dialog>
    );
  };


