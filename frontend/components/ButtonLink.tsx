import { useRouter } from "next/router";
import React from "react";
interface buttonProps {
  title: string;
  link: string;
}
function ButtonLink({ title, link }: buttonProps) {
  const router = useRouter();
  return (
    <button className="relative z-20 group" onClick={() => router.push(link)}>
      <p className="text-xl text-white ">{title}</p>
      <hr className=" absolute w-0 group-hover:w-full smooth-transition" />
    </button>
  );
}

export default ButtonLink;
