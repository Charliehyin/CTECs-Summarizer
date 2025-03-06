import React, { useState } from "react";
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID; // Ensure it's prefixed with REACT_APP_ for CRA

const GoogleAuth = () => {
  const [user, setUser] = useState(null);
  const [error, setError] = useState(null);

  const handleSuccess = (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);
    console.log("Decoded JWT:", decoded);

    // Verify domain - Allow "northwestern.edu" and any subdomain like "u.northwestern.edu"
    if (decoded.hd && decoded.hd.endsWith("northwestern.edu")) {
      setUser({
        name: decoded.name,
        email: decoded.email,
        picture: decoded.picture,
      });
    } else {
      setError("Only users from northwestern.edu and its subdomains can log in.");
    }
  };

  return (
    <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
      <div>
        {!user ? (
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => setError("Login Failed")}
          />
        ) : (
          <div>
            <h3>Welcome, {user.name}</h3>
            <img src={user.picture} alt="User profile" width="50" />
            <p>Email: {user.email}</p>
          </div>
        )}
        {error && <p style={{ color: "red" }}>{error}</p>}
      </div>
    </GoogleOAuthProvider>
  );
};

export default GoogleAuth;
