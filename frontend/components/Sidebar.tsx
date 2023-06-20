import Image from "next/image";
import React, { Dispatch, SetStateAction, useState } from "react";
import ButtonLink from "./ButtonLink";
interface SidebarProps {
  show: boolean;
  setshow: Dispatch<SetStateAction<boolean>>;
}
const Sidebar = ({ show, setshow }: SidebarProps) => {
  return (
    <div
      className={`fixed z-40  lg:hidden  px-16 flex flex-col inset-y-0 ${
        show ? " right-0 " : " -right-[264px]"
      } smooth-transition justify-center bg-[#1a5268] shadow-lg rounded-l-2xl shadow-white space-y-16`}
    >
      <button
        className="absolute top-5 left-1 hover:scale-105 smooth-transition"
        onClick={() => setshow(false)}
      >
        <svg
          width="70"
          height="70"
          viewBox="0 0 96 96"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          xmlnsXlink="http://www.w3.org/1999/xlink"
        >
          <rect width="96" height="96" fill="url(#pattern0)" />
          <defs>
            <pattern
              id="pattern0"
              patternContentUnits="objectBoundingBox"
              width="1"
              height="1"
            >
              <use xlinkHref="#image0_60_3" transform="scale(0.0104167)" />
            </pattern>
            <image
              id="image0_60_3"
              width="70"
              height="70"
              xlinkHref="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAYAAADimHc4AAAABmJLR0QA/wD/AP+gvaeTAAADgUlEQVR4nO2dy2oUQRhGTxnUheIMPoF7FQmIe+PEoK9hwLUvooIoCvockovZa4JxoXtxr0QTN0L8XHQbBnLrukxXdfd/1vmriu9Md6arqqfAMAzDMAzDMAzDMAzDGAoutgFJ14Fl4A5wBbgQ22bh/Aa+AuvAa+fc55jGggVIOg88AR4CZ2IG0WH+Ai+BR865PyENBAmow38L3A6p7yEbwL0QCaGf3KdY+NMsAI9DCr2vgPqe/4nh3naOYx+44Zz74lMUEuJyYF3fmQMe+BaFBDkJqBkKi74FIbegXeCib91A2HXOXfIpCBEg35oh4ZzzytTu5ZkxAZkxAZkxAZkxAZkxAZkxAZkpQcBP4C7wocU+t6me6H+02GcalJYdSbfqdkeS3idu/yg+Srpc9zkv6XvKxrsk4CD8qbZnLeEg/Kk+k0roioBD4bcg4VD4U30mkzDb9Eki4Njwp/pILeHY8Kf6TCIhbdpHDzSWRtPZksaSNhP0tylp3LDPSWxncek2G2Qsp34ap/qKvRLa7EtSNwRI7QTTevhSdwRIsw0oS/hStwRIswkqW/hS9wRIaQPLGr7UTQFSmuCyhy91V4AUF2AR4Uv+AkpblN8GJs65UyfJJI2AVeBsQM2JD4Ix+C7KlyYAYAtYdM7tNBjLGMDjb9eAm9EjPIE+CACPK6EJbXzy/9OXbSnzwHrT+/pJtBl+CKUKgAQSSg8fyhYAERK6ED6ULwACJHQlfOiGgF7TBQHe34icczkW+oMoXUDw19GuSChZQPSzQBcklCog2YNY6RJKFLAFLDSc2xmrwXpvLWGpbrsoShOwDSw1nNsZASvARpOvqHWbEwq9Ehozq2lcDXQ62psZjdsWZJoygzHbkqQPicdri/K+JByrbUsJIdE4bWNWKAnGaFsTY4gdoGxzbhzxedj29Ciio6iwFzRCSTHIGntFKbMAyV7Syz4ZNwJWVP1jXqedNdz5qT43gOitLzGUujGrs/RlY9ZgMAGZMQGZMQGZMQGZMQGZMQGZCRGwl3wU/eGXb0GIgG8BNUPBO5sQAWsBNUNh1bcgZCriGtXP18/51vacdn6+vj4z5ZVv3QB44Rs+hB9hco7qCJOFkPoe8g6439oRJnVH94DnVJfeUNkHnhEYPqQ5xuoq1ckRi1THWPX9bIE9qmOs1oA3IbcdwzAMwzAMwzAMwzAMY5j8AxN6zJ05qZYYAAAAAElFTkSuQmCC"
            />
          </defs>
        </svg>
      </button>
      <ButtonLink title="Home" link="/" />
      <ButtonLink title="Dashboard" link="/dashboard" />
    </div>
  );
};
export default Sidebar;
