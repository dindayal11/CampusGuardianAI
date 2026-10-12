"use client";
import { FormEvent,useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
export default function PlatformAccess(){
 const router=useRouter();const[email,setEmail]=useState("");const[password,setPassword]=useState("");const[error,setError]=useState("");
 async function submit(e:FormEvent){e.preventDefault();setError("");try{await apiFetch("/auth/platform-login",{method:"POST",body:JSON.stringify({email,password})});router.push("/dashboard/platform");}catch(e){setError(e instanceof Error?e.message:"Login failed.");}}
 return <main className="auth-wrap"><div className="auth"><span className="eyebrow">Restricted access</span><h1>Platform administration.</h1><p className="muted">This route is intentionally not linked from the public navigation.</p><form onSubmit={submit}><div className="field"><label>Email</label><input type="email" required autoComplete="username" value={email} onChange={e=>setEmail(e.target.value)}/></div><div className="field"><label>Password</label><input type="password" required autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)}/></div>{error&&<div className="notice">{error}</div>}<div className="cta"><button className="btn primary" type="submit">Sign in</button></div></form></div></main>
}
