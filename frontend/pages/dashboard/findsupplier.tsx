import Link from "next/link";
import React from "react";
import DashbordSideBar from "../../components/DashboardSideBar";
import Footer from "../../components/Footer";
import { motion } from "framer-motion";
import FindSupplier from "../../components/DashbordElements/FindSupplier";

function Findsupplier() {
  return (
    <>
      <div className="relative flex overflow-hidden">
        <DashbordSideBar />

        <div className="p-5 min-h-screen w-full bg-gray-100 ">
          <FindSupplier />
        </div>
      </div>
      <Footer />
    </>
  );
}

export default Findsupplier;
