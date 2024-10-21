import React ,{createContext, useContext,useState,useEffect} from "react";
import { DataTable } from "primereact/datatable";
import { Column } from "primereact/column";
import { Button } from 'primereact/button';
import { Popup } from "./popup";
import 'primereact/resources/themes/saga-blue/theme.css';  // You can choose any theme here
import 'primeicons/primeicons.css';
import { fetchSlots } from "./service/slotapi";
import { bookslot } from "./service/userapi";
import './slot.css'
import Cookies from 'js-cookie';

export const clickedBtn = createContext()


export function Slot (){
    //const slots = { "12/02/2024": {"12:00":1,"01:00":4,"22:00":1,"21:00":4,"11:00":1,"02:00":4,"03:00":1,"04:00":4,"07:00":4,"09:00":4},"11/02/2024": {"12:00":1,"01:00":4},"10/02/2024": {"12:00":1,"01:00":4}}
    const [role,setRole] = useState( ()=>{return Cookies.get("role")})
    const [slots,setSlots] = useState({});
    const [data , setData] = useState();
    const [visible, setVisible] = useState(false);
    function btnClick (functionality) {
        let data = {}
        data['label'] = functionality
        data['data'] = slots
        setData(data)
        setVisible(true)
        
    }
  
    const fetchSlotsData = async () => {
      const data = await fetchSlots();
      setSlots(data);
  };

  useEffect(() => {
      if (!visible) {
          fetchSlotsData();
      }
  }, [visible]);

      const bookslotcall = async(date,time)=>{
        let req ={
            "date":date,"time":time
        }
            try{
            let response = await bookslot(req)
            fetchSlotsData();
            alert(response.message)
            }catch   (Error){
            alert("Error Occured")
            }
        
      } 

      return (
        <clickedBtn.Provider value = {{data,setData}}>
        <div style={{border:"1px solid black" , "padding":"2%"}}>
            <div style={{"display":"flex","justifyContent":"space-around"}}>
            <h1>Slots</h1>
            {role!="user" && <div style = {{justifyContent:"space-around"}}>
                <Button onClick={()=>btnClick("Add")} style={{margin:"12px"}} icon="pi-plus" label="Add" />
                <Button onClick={()=>btnClick("Edit")} style={{margin:"12px"}} icon="pi pi-pencil" label="Edit" />
                </div>}
            </div>
            
            <div >
            { Object.entries (slots).map(([key,val],a)=>(
               <div style={{"background":"#f9f9f9","border":"1px solid #ddd" ,"borderRadius":"10%","margin-bottom":"2%"}}>
                <div style={{"display":"flex","justifyContent":"space-around"}}>
                <h2>{key}</h2>
              
                </div>
                  
                 <div style={{"display":"flex" ,"justifyContent":"start","flex-wrap":"wrap"}} key={a}>
                  
                    {Object.entries(val).map(([time,qty],k)=>(
                    <div onClick={() => console.log(time)} id={k}
                    className="slot-card">
                    <h4 className="slot-time">{time}</h4>
                    <label className="slot-qty">{qty} slots</label>
                    {role == "user" && qty >0&& (
                      <button onClick={()=>{bookslotcall(key,time)}} className="book-button">
                        Book
                      </button>
                    )}
                  </div>   
                    ))}
                </div>
               </div>
            ))}
            
            </div>
            
            {visible && <Popup visible={visible} onHide={() => setVisible(false)} />}
         </div>
         </clickedBtn.Provider>
    
      );
      

}


