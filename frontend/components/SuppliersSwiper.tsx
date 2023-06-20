import "swiper/css";
import React from "react";
import Image from "next/image";
import { motion } from "framer-motion";
import { Autoplay } from "swiper";
import { Swiper, SwiperSlide } from "swiper/react";
import { useInView } from "react-intersection-observer";

function SuppliersSwiper() {
  const { ref, inView, entry } = useInView({
    /* Optional options */
    threshold: 0,
  });
  const Suppliers_LOGOS = [
    "RS.png",
    "Festo_logo.svg.png",
    "Molex-Logo.png",
    "mouser.png",
    "wago.png",
    "dk.webp",
  ];
  return (
    <div
      className="w-full relative  flex flex-col justify-center py-9 cursor-pointer"
      ref={ref}
    >
      <div className="flex justify-center pb-6">
        <motion.h1
          className=" text-4xl text-gray-600 font-bold uppercase"
          animate={{
            y: inView ? "0" : 200,
            opacity: inView ? "1" : "0",
          }}
          transition={{ duration: 0.5 }}
        >
          Trusted Suppliers
        </motion.h1>
      </div>
      <div className=" py-7">
        <Swiper
          modules={[Autoplay]}
          slidesPerView={6}
          loop={true}
          autoplay={{
            delay: 0,
            disableOnInteraction: false,
            pauseOnMouseEnter: false,
            waitForTransition: false,
            stopOnLastSlide: false,
          }}
          speed={2000}
          spaceBetween={5}
          breakpoints={{
            320: { slidesPerView: 2 },
            768: { slidesPerView: 3 },
            1025: { slidesPerView: 6 },
          }}
          className="swiper-wrapper"
        >
          {Suppliers_LOGOS.map((logo, i) => (
            <SwiperSlide key={i}>
              <Image src={`/${logo}`} width={90} height={60} alt={logo} />
            </SwiperSlide>
          ))}
        </Swiper>
      </div>
    </div>
  );
}

export default SuppliersSwiper;
