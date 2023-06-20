import Image from "next/image";
import React, { useState } from "react";
import { motion } from "framer-motion";
import LoginModal from "./LoginModal";

const Banner = () => {
  const [isOpen, setisOpen] = useState(false);
  function openModal() {
    setisOpen(true);
  }
  function closeModal() {
    setisOpen(false);
  }
  const scrollDown = () => {
    window.scrollTo({ top: 1150, behavior: "smooth" });
  };
  return (
    <div className="absolute inset-0 max-h-screen bg-blue-900 ">
      <video
        src="/lastanimation.mp4"
        autoPlay
        muted
        loop
        className="absolute inset-0 h-full w-full object-fill"
      />

      <motion.div
        className="relative max-w-7xl mx-auto  pt-16 pb-24 px-4 sm:py-32 sm:px-6 lg:px-8 text-center "
        initial={{ opacity: 1, y: "100vh" }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-4xl font-poppins tracking-tight  mt-16 sm:mt-2  text-white sm:text-5xl lg:text-6xl pb-4">
          ComplianceGrabber 2.0
        </h1>
        <LoginModal
          isOpen={isOpen}
          openModal={openModal}
          closeModal={closeModal}
        />
        {/* <p className="mt-6 hidden sm:block text-xl text-white font-poppins text-center leading-10">
          You’re digital tool to get all you need in one place and from all the
          best suppliers,we strive to make all the product details available for
          you,coming from the most used and trusted suppliers all around the
          Globe !
        </p> */}
      </motion.div>
      <div className="absolute bottom-5 inset-x-auto w-full mt-[18rem] sm:mt-36 flex justify-center px-2 ">
        <div className="flex flex-col lg:flex-row space-y-4 lg:space-y-0  lg:space-x-2 ">
          <motion.button
            initial={{ opacity: 0, x: "-100vh" }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.6, duration: 0.4 }}
            className="font-poppins  relative  mx-2 overflow-hidden shadow-sm shadow-green-600 hover:bg-gray-400  smooth-transition text-lg group text-white rounded-md inline-flex items-center justify-center space-x-4  py-3 border border-white  min-w-[350px] px-6"
            onClick={openModal}
          >
            <p className="lg:z-10 ">LOGIN</p>
          </motion.button>
          <motion.button
            initial={{ opacity: 0, x: "-100vh" }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.9, duration: 0.4 }}
            className="font-poppins  relative mx-2  overflow-hidden shadow-sm shadow-green-600 hover:bg-gray-400  smooth-transition text-lg group text-white rounded-md inline-flex items-center justify-center space-x-4  py-3 border border-white  min-w-[350px] px-6"
            onClick={scrollDown}
          >
            <p className="lg:z-10 ">GET STARTED</p>
          </motion.button>
        </div>
      </div>
    </div>
  );
};

export default Banner;
