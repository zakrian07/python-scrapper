import React, { useEffect, useState } from 'react';

const ToastErrorPanel = ({ message }) => {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        setIsVisible(true);

        const timer = setTimeout(() => {
            setIsVisible(false);
        }, 3000);

        return () => {
            clearTimeout(timer);
        };
    }, []);

    const toastStyles = {
        backgroundColor: '#FDAEA1',
        color: '#ffffff',
        fontFamily: 'Poppins',
        fontSize: '16px',
        padding: '16px',
        borderRadius: '8px',
        boxShadow: '0 2px 4px rgba(0, 0, 0, 0.2)',
        position: 'fixed',
        top: '80%',
        left: '60%',
        transform: 'translate(-50%, -50%)',
        zIndex: 100,
        opacity: isVisible ? 1 : 0,
        pointerEvents: isVisible ? 'auto' : 'none',
        transition: 'opacity 300ms',
        display: 'flex',
        alignItems: 'center',
    };

    const iconStyles = {
        width: '24px',
        height: '24px',
        marginRight: '8px',
    };

    return (
        <div className="flex w-full justify-center h-full items-center absolute inset-0">
            <div style={toastStyles}>
                <svg xmlns="http://www.w3.org/2000/svg" style={iconStyles} viewBox="0 0 24 24" fill="none" stroke="#ffffff" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12" y2="16" />
                </svg>
                <span className="font-bold">{message}</span>
            </div>
        </div>
    );
};

export default ToastErrorPanel;
