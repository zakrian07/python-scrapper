import Image from "next/image";
import React from "react";
import { Carousel } from "react-responsive-carousel";
import DahbordHeader from "./DahboardHeader";

import StatCard from "./StatCard";
import SupplierList from "./supllierSection/SupplierList";

function Overview() {
  return (
    <div>
      {/* Top section */}
      <DahbordHeader title="Overview" />
      {/* End top section */}
      <div className="container mx-auto">
        <div className="w-full mt-16 p-5 grid grid-cols-1  md:grid-cols-3 gap-4 gaps-x-4 xl:gap-x-24 ">
          <StatCard
            title="Total number of suppliers"
            quantity={43}
            src="supplierCard.png"
          />
          <StatCard title="Manufacturers" quantity={32} src="manufCard.png" />
          <StatCard
            title="Distributers"
            quantity={11}
            src="distributerCard.png"
          />
        </div>

        <div className="lg:flex mt-4 p-5">
          <div className="w-full">
            {/* Map component */}
            <div className="relative rounded-lg bg-white flex justify-end  min-h-[500px] p-5">
              <p className="absolute left-5 bottom-5 text-[#225373] text-xl font-semibold">
                Total Number of Suppliers
              </p>
              <img src="/map.png" className="w-[85%] h-[85%]" />
            </div>
            {/* suppliers sections */}
            <div className="grid  grid-cols-1 md:grid-cols-2 gap-9 mt-9">
              <SupplierList
                title="Manufacturers"
                suppliers={[
                  { logo: "/RS.png", quantity: 64 },
                  { logo: "/RS.png", quantity: 64 },
                  ,
                  { logo: "/RS.png", quantity: 64 },
                  ,
                  { logo: "/RS.png", quantity: 64 },
                ]}
              />

              <SupplierList
                title="Distributors"
                suppliers={[
                  { logo: "/RS.png", quantity: 64 },
                  { logo: "/RS.png", quantity: 64 },
                  ,
                  { logo: "/RS.png", quantity: 64 },
                  ,
                  { logo: "/RS.png", quantity: 64 },
                ]}
              />
            </div>
          </div>
          <div className="min-w-[350px] space-y-10 mt-9 md:mt-0 md:ml-9">
            <div className=" w-full p-4 bg-white rounded-lg shadow">
              <h1 className="text-sm text-gray-500">
                # of Product provided by suppliers
              </h1>
              <p className="text-4xl  mt-4 leading-tight font-bold text-[#225373]">
                N/A
              </p>

              <img src="/Vector95.png" className="w-full" />
            </div>
            <div className=" w-full p-4 bg-white rounded-lg shadow">
              <h1 className="text-sm text-gray-500">
                N/A
              </h1>
              <p className="text-4xl  mt-4 leading-tight font-bold text-[#225373]">
                N/A
              </p>

              <img src="/Vector95.png" className="w-full" />
            </div>

            <div className=" w-full bg-white flex  flex-col justify-center rounded-lg  items-center p-5">
              <img src="/circles.png" className="w-[70%] h-[70%]" />
              <p className="text-4xl  mt-4 leading-tight font-bold text-[#225373]">
                N/A
              </p>
              <p className="text-sm text-gray-500">User activity</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default Overview;
