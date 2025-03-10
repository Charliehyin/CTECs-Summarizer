import React, { useState } from 'react';
import nuLogo from '../assets/northwestern-logo.png';
import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

const GOOGLE_CLIENT_ID = process.env.REACT_APP_GOOGLE_CLIENT_ID;

const Login = ({ onLogin }) => {
  const [error, setError] = useState(null);

  const handleSuccess = (credentialResponse) => {
    console.log("Google login success:", credentialResponse);
    
    try {
      const decoded = jwtDecode(credentialResponse.credential);
      console.log("Decoded JWT:", decoded);

      // Verify domain - Allow "northwestern.edu" and any subdomain like "u.northwestern.edu"
      if (decoded.hd && decoded.hd.endsWith("northwestern.edu")) {
        onLogin({
          name: decoded.name,
          email: decoded.email,
          picture: decoded.picture,
        });
      } else {
        console.log("Domain verification failed:", decoded.hd);
        setError("Only users from northwestern.edu and its subdomains can log in.");
      }
    } catch (err) {
      console.error("JWT decode error:", err);
      setError("Failed to process login information.");
    }
  };

  const handleError = (error) => {
    console.error("Google login error:", error);
    setError("Login Failed. Please try again.");
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-logo">
          <img src={nuLogo} alt="Northwestern University" />
        </div>

        <h1 className="login-title">Welcome to the Northwestern CTECs Assistant</h1>
        
        <p className="login-description">
          Your AI-powered guide to Northwestern University courses
        </p>
        
        <div className="login-divider">
          <span>Sign in with your Northwestern email</span>
        </div>
        
        {GOOGLE_CLIENT_ID ? (
          <GoogleOAuthProvider clientId={GOOGLE_CLIENT_ID}>
            <div className="google-login-wrapper">
              <GoogleLogin
                onSuccess={handleSuccess}
                onError={handleError}
                theme="outline"
                size="large"
                text="signin_with"
                shape="rectangular"
                logo_alignment="left"
              />
            </div>
          </GoogleOAuthProvider>
        ) : (
          <div className="google-login-error">
            Google login configuration is missing.
          </div>
        )}
        
        {error && <p className="login-error">{error}</p>}
        
        <p className="login-note">
          Only Northwestern University emails (@u.northwestern.edu) are supported
        </p>
      </div>
    </div>
  );
};

export default Login; 