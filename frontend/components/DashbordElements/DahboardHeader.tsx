import React from "react";
import ProfileDropdown from "./ProfileDropdown";

interface NavProps {
  title: string;
}

function DahbordHeader({ title }: NavProps) {
  return (
    <div>
      <div className="flex justify-between">
        <h1 className="text-2xl font-bold text-gray-600">{title}</h1>
        <ProfileDropdown />
      </div>
      <hr className="mt-5" />
    </div>
  );
}

export default DahbordHeader;
