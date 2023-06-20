// import React, { useState, useEffect } from "react";

// const ProgressBar = () => {
//     const [progress, setProgress] = useState(0);
//     useEffect(() => {
//         const timer = setInterval(() => {
//             // Generate random number between 1 and 10
//             const randomIncrement = Math.floor(Math.random() * 10) + 1;
//             setProgress((prevProgress) => {
//                 const newProgress = prevProgress + randomIncrement;
//                 return newProgress > 100 ? 99 : newProgress;
//             });
//         }, 1000);

//         return () => {
//             clearInterval(timer);
//         };
//     }, []);

//     return (
//         <div className="w-full   bg-gradient-to-t from-[#d4d4d4] to-[#9a9a9a] h-2 rounded">
//             <div
//                 className="sidebar-color h-full"
//                 style={{ width: `${progress}%` }}
//             >{progress}</div>
//         </div>
//     );
// };

// export default ProgressBar;

import React, { useState, useEffect } from "react";
import { CircularProgressbar, buildStyles } from "react-circular-progressbar";
import "react-circular-progressbar/dist/styles.css";

const WheelProgressBar = ({ progressCompleted }) => {
    const [progress, setProgress] = useState(0);



    useEffect(() => {
        const interval = setInterval(() => {

            if (progress < 100) {
                const randomProgress = Math.floor(Math.random() * 5) + 1;
                setProgress((prevProgress) => {
                    let newProgress = prevProgress + randomProgress;
                    if (progressCompleted) {
                        return 100
                    } else {
                        return newProgress > 95 ? 98 : newProgress;
                    }
                });
            } else {
                clearInterval(interval);
            }
        }, 500);

        return () => clearInterval(interval);
    }, [progressCompleted]);

    return (
        <div className="flex justify-center items-center h-screen">
            <div style={{ width: "200px" }}>
                <CircularProgressbar
                    value={progress}
                    text={`${progress}%`}
                    styles={buildStyles({
                        textSize: "20px",
                        pathColor: `rgba(${225 - (progress * 2)}, ${progress * 2}, 0, 1)`,
                        textColor: "#333",
                        trailColor: "#f4f4f4",
                        backgroundColor: "#eaeaea",
                    })}
                />
            </div>
        </div>
    );
};




export default WheelProgressBar;




