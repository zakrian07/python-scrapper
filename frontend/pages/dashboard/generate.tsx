import React, { useState } from "react";
import Generate from "../../components/DashbordElements/Generate";
import DashbordSideBar from "../../components/DashboardSideBar";
import Footer from "../../components/Footer";

function generate() {
  return (
    <>
      <div className="relative flex overflow-hidden">
        <DashbordSideBar />

        <div className="p-5 min-h-screen w-full bg-gray-100 ">
          <Generate />
        </div>
      </div>
      <Footer />
    </>
  );
}

export default generate;
