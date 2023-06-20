import { NextPage } from "next";
import Link from "next/link";
import React, { useState } from "react";

import Image from "next/image";
import "react-responsive-carousel/lib/styles/carousel.min.css"; // requires a loader
import { Carousel } from "react-responsive-carousel";
import DashbordSideBar from "../../components/DashboardSideBar";
import Overview from "../../components/DashbordElements/Overview";
import Footer from "../../components/Footer";

const Suppliers: NextPage = () => {
  return (
    <>
      <div className="relative flex overflow-hidden">
        <DashbordSideBar />

        <div className="p-5 minh-screen w-full bg-gray-100  ">
          <Overview />
        </div>
      </div>

      <Footer />
    </>
  );
};

export default Suppliers;
