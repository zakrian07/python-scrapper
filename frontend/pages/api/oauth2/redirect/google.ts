import { NextApiRequest, NextApiResponse } from "next";
import nextConnect from "next-connect";
import passport from "../../../../lib/passport-google-auth";

export default nextConnect().get(
    passport.authenticate("google"),
    (req: NextApiRequest & { user: any }, res: NextApiResponse) => {
        // you can save the user session here. to get access to authenticated user through req.user
        res.redirect("/");
    }
);