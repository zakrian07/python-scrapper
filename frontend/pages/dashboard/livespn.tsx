import React from "react";
import LiveSpn from "../../components/DashbordElements/LiveSpn";
import DashbordSideBar from "../../components/DashboardSideBar";
import Footer from "../../components/Footer";

function livespn() {
  return (
    <>
      <div className="relative flex overflow-hidden">
        <DashbordSideBar />

        <div className="px-2 py-5 min-h-screen  w-full bg-gray-100 ">
          <LiveSpn />
        </div>
      </div>
      <Footer />
    </>
  );
}

export default livespn;
