import { ArrowTopRightOnSquareIcon } from "@heroicons/react/20/solid";
import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
function TutorialSection() {
  const [Appeared, setAppeared] = useState(false);
  const { ref, inView, entry } = useInView({
    /* Optional options */
    threshold: 0,
  });
  useEffect(() => {
    if (inView == true) setAppeared(true);
    return () => setAppeared(false);
  }, [inView]);
  return (
    <div ref={ref} className="w-full py-16 bg-[#28546df5] bg-blend-color-burn">
      <div className="container mx-auto grid grid-cols-1 md:grid-cols-2 min-h-[500px] px-4">
        <motion.div
          animate={{
            x: inView ? "0" : -500,
            opacity: inView ? "1" : "0",
          }}
          transition={{ duration: 0.5 }}
          className="py-16 space-y-6 flex flex-col justify-center"
        >
          <h1 className="text-5xl font-poppins text-white">
            How does it work ?
          </h1>
          <p className="text-xl  text-white max-w-[500px]">
            we trie to make the usage as user friendly as possible, to learn
            more about how to use our tools watch this tutorial
          </p>
          <div className="mt-8  ">
            <div className="inline-flex cursor-pointer rounded-md shadow-lg hover:scale-x-110 smooth-transition">
              <a
                href="#"
                className="inline-flex items-center justify-center px-5 py-3 border border-transparent text-base font-medium rounded-md text-gray-900 bg-white hover:bg-gray-50"
              >
                Try Our Features Now !
                <ArrowTopRightOnSquareIcon
                  className="-mr-1 ml-3 h-5 w-5 text-gray-400"
                  aria-hidden="true"
                />
              </a>
            </div>
          </div>
        </motion.div>
        <motion.div
          className={`rounded-xl overflow-hidden min-h-[500px]`}
          animate={{
            x: inView ? "0" : Appeared ? 0 : 300,
            opacity: inView ? "1" : "0",
          }}
          transition={{ duration: 0.5 }}
        >
          <iframe
            className="w-full h-full"
            src="https://www.youtube.com/embed/MAtaT8BZEAo"
            title="Parent Teacher Interviews"
            frameBorder="0"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </motion.div>
      </div>
    </div>
  );
}

export default TutorialSection;
