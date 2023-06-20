import React, { useEffect, useState } from "react";
import {
  ArrowPathIcon,
  CloudArrowUpIcon,
  CogIcon,
  LockClosedIcon,
  ServerIcon,
  ShieldCheckIcon,
} from "@heroicons/react/24/outline";
import { motion } from "framer-motion";
import { useInView } from "react-intersection-observer";
function FeatureSection() {
  const [Appeared, setAppeared] = useState(false);
  const { ref, inView, entry } = useInView({
    /* Optional options */
    threshold: 0,
  });
  const features = [
    {
      name: "Push to Deploy",
      description:
        "Ac tincidunt sapien vehicula erat auctor pellentesque rhoncus. Et magna sit morbi lobortis.",
      icon: CloudArrowUpIcon,
    },
    {
      name: "SSL Certificates",
      description:
        "Ac tincidunt sapien vehicula erat auctor pellentesque rhoncus. Et magna sit morbi lobortis.",
      icon: LockClosedIcon,
    },
    {
      name: "Simple Queues",
      description:
        "Ac tincidunt sapien vehicula erat auctor pellentesque rhoncus. Et magna sit morbi lobortis.",
      icon: ArrowPathIcon,
    },
    {
      name: "Advanced Security",
      description:
        "Ac tincidunt sapien vehicula erat auctor pellentesque rhoncus. Et magna sit morbi lobortis.",
      icon: ShieldCheckIcon,
    },
    {
      name: "Powerful API",
      description:
        "Ac tincidunt sapien vehicula erat auctor pellentesque rhoncus. Et magna sit morbi lobortis.",
      icon: CogIcon,
    },
    {
      name: "Database Backups",
      description:
        "Ac tincidunt sapien vehicula erat auctor pellentesque rhoncus. Et magna sit morbi lobortis.",
      icon: ServerIcon,
    },
  ];
  useEffect(() => {
    if (inView == true) setAppeared(true);
    return () => setAppeared(false);
  }, [inView]);
  return (
    <motion.div
      ref={ref}
      className="relative bg-[#203058] py-16 shadow-xl shadow-[#2c4a5cf5]"
    >
      <div className="mx-auto max-w-md px-4 text-center sm:max-w-3xl sm:px-6 lg:max-w-7xl lg:px-8">
        <motion.h2
          animate={{
            y: inView ? "0" : 200,
            opacity: inView ? "1" : "0",
          }}
          transition={{ duration: 0.6 }}
          className="font-poppins text-5xl text-white"
        >
          Features
        </motion.h2>
        <div className="mt-12">
          <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature, i) => (
              <motion.div
                key={feature.name}
                className="pt-6"
                animate={{
                  x: inView ? "0" : i % 2 == 0 ? 200 : -200,
                  opacity: inView ? "1" : "0",
                }}
                transition={{ duration: 0.7 }}
              >
                <div className="flow-root rounded-lg bg-gray-50 px-6 pb-8 group cursor-pointer shadow-md shadow-indigo-600">
                  <div className="-mt-6">
                    <div>
                      <span className="inline-flex items-center justify-center rounded-md bg-indigo-800 group-hover:bg-indigo-600 p-3 shadow-lg smooth-transition">
                        <feature.icon
                          className="h-6 w-6 text-white"
                          aria-hidden="true"
                        />
                      </span>
                    </div>
                    <h3 className="mt-8 text-lg font-medium tracking-tight text-gray-900">
                      {feature.name}
                    </h3>
                    <p className="mt-5 text-base text-gray-500">
                      {feature.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </motion.div>
  );
}

export default FeatureSection;
