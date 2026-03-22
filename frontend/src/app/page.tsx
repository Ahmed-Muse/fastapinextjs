//import AppLayout from "../components/AppLayout"; 
"use client"
import Side_Top_Navbar_Layout from "../components/layout/navbars/navbars";
import Card from "../components/cards/card";
import Button from "../components/buttons/button";
import { use, useState } from "react";
export default function HomePage() {
  const [ahmed_counter,setAhmed_counter]=useState(10);
  return (
    <Side_Top_Navbar_Layout>
         
          <button onClick={()=>setAhmed_counter(ahmed_counter+10)}>+</button>
          <span className="mx-4">{ahmed_counter}</span>
          <button onClick={()=>setAhmed_counter(ahmed_counter-10)}>-</button>
         
      <div>
      
        <h1 className="text-2xl font-bold mb-4">Dashboard Overview</h1>
        <p>Welcome to the AI Product Sizing Engine.</p>
      </div>
      <Card>
        <h2 className="text-xl font-semibold mb-2">Card Title</h2>
        <p>This is some content inside the card. You can put anything you  <Button>Click me</Button> want here!</p>
     
      </Card>
      <Button>Click me</Button>
    </Side_Top_Navbar_Layout>
  );
}