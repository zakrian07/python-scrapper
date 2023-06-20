import React from "react";
import { motion } from "framer-motion";
import Image from "next/image";
interface CardProps {
  title: string;
  quantity: number;
  src: string;
}

function StatCard({ title, quantity, src }: CardProps) {
  return (
    <motion.div
      initial={{ opacity: 1, y: "100vh" }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="rounded-md  relative overflow-hidden border min-h-[250px] shadow-lg text-center p-4 cursor-pointer"
    >
      <Image src={`/${src}`} layout="fill" className="object-center" />
      <div className="absolute left-4 bottom-6 z-10 flex flex-col items-start pl-2">
        <p className="text-5xl  font-bold text-white ">{quantity}</p>
        <h1 className="font-poppins text-sm text-white mt-1">{title}</h1>
      </div>
    </motion.div>
  );
}

export default StatCard;
