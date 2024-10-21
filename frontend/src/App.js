import logo from './logo.svg';
import './App.css';
import React,{useState} from 'react';
import {Menu} from './Menu'
import {Home} from './Home'
import {Slot} from './Slot'
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PrimeReactProvider, PrimeReactContext } from 'primereact/api';
import 'primereact/resources/primereact.min.css';   
  import 'primereact/resources/themes/saga-blue/theme.css';  // You can choose any theme here
import 'primereact/resources/primereact.min.css';    
import 'primeicons/primeicons.css';
function App() {
  
  

  return (
  
    <BrowserRouter>
    <Routes>
    <Route path="/" element={<Home />}>
    <Route path="menu" element={<Menu />} />
    <Route path="slot" element={<Slot />} />
    </Route>
    </Routes>
    </BrowserRouter>


    
  );
}

export default App;




