import React from "react";
import { Dialog, Transition } from "@headlessui/react";
import { Fragment, useState } from "react";
import Image from "next/image";
import Link from "next/link";

interface modalProps {
  isOpen: boolean;
  openModal: () => void;
  closeModal: () => void;
}

function LoginModal({ openModal, closeModal, isOpen }: modalProps) {
  return (
    <>
      <Transition appear show={isOpen} as={Fragment}>
        <Dialog as="div" className="relative z-10" onClose={closeModal}>
          <Transition.Child
            as={Fragment}
            enter="ease-out duration-300"
            enterFrom="opacity-0"
            enterTo="opacity-100"
            leave="ease-in duration-200"
            leaveFrom="opacity-100"
            leaveTo="opacity-0"
          >
            <div className="fixed inset-0 bg-black bg-opacity-25" />
          </Transition.Child>

          <div className="fixed inset-0 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center py-8 px-3 text-center">
              <Transition.Child
                as={Fragment}
                enter="ease-out duration-300"
                enterFrom="opacity-0 scale-95"
                enterTo="opacity-100 scale-100"
                leave="ease-in duration-200"
                leaveFrom="opacity-100 scale-100"
                leaveTo="opacity-0 scale-95"
              >
                <Dialog.Panel className="w-full max-w-sm transform overflow-hidden rounded-2xl bg-white p-9 text-left align-middle shadow-xl transition-all">
                  <Dialog.Title
                    as="h3"
                    className="text-2xl   text-center font-poppins leading-6 text-gray-900"
                  >
                    <div className="flex justify-center items-center flex-col">
                      <Image src="/logo.png" width="90" height="90" />
                      <p className="text-xl  text-gray-600 mb-4">
                        ComplianceGrabber 2.0
                      </p>
                      <p className=" font-semibold text-lg tracking-wider mb-1">
                        Log in to ComplianceGrabber 2.0
                      </p>
                      <p className="text-sm font-medium text-gray-500 tracking-tight">
                        Enter your email and password below
                      </p>
                    </div>
                  </Dialog.Title>
                  {/* <div className="mt-2">
                    <div>
                      <label className="block text-sm font-poppins text-gray-500">
                        Email
                      </label>
                      <div className="">
                        <input
                          type="email"
                          name="email"
                          id="email"
                          className="block ml-1 w-full px-4 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          placeholder="Email address"
                          aria-describedby="email-description"
                        />
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-poppins text-gray-500 mt-3">
                        Password
                      </label>
                      <div className="">
                        <input
                          type="password"
                          name="email"
                          className="block ml-1 w-full px-4 rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                          placeholder="password"
                          aria-describedby="password-description"
                        />
                      </div>
                    </div>
                  </div> */}

                  <div className="mt-4">
                    <Link href="/api/login" passHref>
                      <button
                        type="button"
                        className="inline-flex w-full bg-blue-700 justify-center rounded-lg text-white border border-transparent  py-2 text-sm font-poppins   focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                        onClick={closeModal}
                      >
                        Login
                      </button>
                    </Link>

                  </div>
                </Dialog.Panel>
              </Transition.Child>
            </div>
          </div>
        </Dialog>
      </Transition>
    </>
  );
}

export default LoginModal;
