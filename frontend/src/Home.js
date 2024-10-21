import { PrimeReactProvider, PrimeReactContext } from 'primereact/api';
import { Button } from 'primereact/button';
import { Menu } from './Menu';
import  {Slot} from './Slot';
import { useState ,useEffect} from 'react';
import  {USserLogin} from './userlogin';
import Cookies from 'js-cookie';
export function Home (){
    const [isMenu,setIsMenu] = useState(false)
    const [isSlot,setIsSlot] = useState(false)
    const [jwt,setJwt] = useState(() => Cookies.get("authToken") ||  null);
    const [role,setrole] = useState(() => Cookies.get("role") || null)// make || null
    useEffect(() => {
      if (jwt) {
          Cookies.set("authToken",jwt,{ expires: 1 }); // Store for 1 day
          Cookies.set("role",role, { expires: 1 }); 
          console.log("he",Cookies.get("role"))
        } else {
          Cookies.remove("authToken")
          Cookies.remove("role"); // Remove token if user logs out
          setIsMenu(false);
          setIsSlot(false);
        }
  }, [jwt]);
    return (
        <PrimeReactProvider>
          <div style={{ textAlign: 'center', marginTop: '50px' }}>
          <h1>Welcome to HTRSM</h1>
          {!jwt && <USserLogin setToken ={(token)=>setJwt(token)} setRole={(role)=>setrole(role)}></USserLogin>}
          {jwt && <div>
          <Button label="Menu"  onClick={()=>getMenu()}/>
          <Button label='Slots' onClick={()=>getSlots()}/>
          <Button label='Logout' onClick={()=>setJwt(null)}></Button>
          
        {isSlot && <Slot ></Slot>}
        {isMenu && <Menu role= {role}></Menu>}
          </div>}
        </div>
        </PrimeReactProvider>

     
      );
      function getMenu(){
        setIsMenu(true)
        setIsSlot(false)
      }
      function getSlots(){
        setIsMenu(false)
        setIsSlot(true)
      }
      
}