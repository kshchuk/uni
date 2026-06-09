# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""Exp 3: Taylor-Green Vortex decay, pseudo-spectral PyTorch solver."""
from __future__ import annotations
import argparse, shutil
from pathlib import Path
import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import torch

OUTPUT_DIR = Path(__file__).resolve().parent / "figures"

def get_device():
    if torch.backends.mps.is_available():
        d = torch.device("mps"); print(f"Device: {d} (Apple Silicon GPU)"); return d
    print("WARNING: MPS unavailable, CPU"); return torch.device("cpu")

def get_writer(fps):
    if shutil.which("ffmpeg"):
        try: return animation.FFMpegWriter(fps=fps, bitrate=2500), ".mp4"
        except: pass
    print("УВАГА: ffmpeg не знайдено. Зберігаємо .gif."); return animation.PillowWriter(fps=fps), ".gif"

def fftn_safe(x):
    if x.device.type == "mps":
        try: return torch.fft.fftn(x, dim=(-3,-2,-1))
        except: return torch.fft.fftn(x.cpu(), dim=(-3,-2,-1)).to(x.device)
    return torch.fft.fftn(x, dim=(-3,-2,-1))

def ifftn_safe(x):
    if x.device.type == "mps":
        try: return torch.fft.ifftn(x, dim=(-3,-2,-1)).real
        except: return torch.fft.ifftn(x.cpu(), dim=(-3,-2,-1)).real.to(x.device)
    return torch.fft.ifftn(x, dim=(-3,-2,-1)).real

class TaylorGreenSolver:
    def __init__(self, n, nu, L, device):
        self.n, self.nu, self.L, self.device = n, nu, L, device
        x1d = torch.linspace(0, L, n, device=device)
        x,y,z = torch.meshgrid(x1d,x1d,x1d, indexing='ij')
        self.u = torch.sin(x)*torch.cos(y)*torch.cos(z)
        self.v = -torch.cos(x)*torch.sin(y)*torch.cos(z)
        self.w = torch.zeros_like(self.u)
        self._build_ops()
        self.u,self.v,self.w = self.project(self.u,self.v,self.w)

    def _build_ops(self):
        n,L = self.n,self.L
        k1d = 2*np.pi * torch.fft.fftfreq(n, d=L/n, device=self.device)  # кутові хвильові числа 2*pi*m/L
        kx,ky,kz = torch.meshgrid(k1d,k1d,k1d, indexing='ij')
        self.kx,self.ky,self.kz = kx,ky,kz
        self.k2 = kx*kx+ky*ky+kz*kz; self.k2[0,0,0]=1.0
        km=n//3; sc=2*np.pi/L
        self.mask = ((kx.abs()<=km*sc)&(ky.abs()<=km*sc)&(kz.abs()<=km*sc)).float()

    def project(self,u,v,w):
        uh,vh,wh = fftn_safe(u),fftn_safe(v),fftn_safe(w)
        ku = self.kx*uh+self.ky*vh+self.kz*wh
        uh -= self.kx*ku/self.k2; vh -= self.ky*ku/self.k2; wh -= self.kz*ku/self.k2
        return ifftn_safe(uh),ifftn_safe(vh),ifftn_safe(wh)

    def d(self,f,k): return ifftn_safe(1j*k*fftn_safe(f))

    def nonlinear(self,u,v,w):
        ux,uy,uz = self.d(u,self.kx),self.d(u,self.ky),self.d(u,self.kz)
        vx,vy,vz = self.d(v,self.kx),self.d(v,self.ky),self.d(v,self.kz)
        wx,wy,wz = self.d(w,self.kx),self.d(w,self.ky),self.d(w,self.kz)
        return (-(u*ux+v*uy+w*uz), -(u*vx+v*vy+w*vz), -(u*wx+v*wy+w*wz))

    def dealias(self,u,v,w):
        m=self.mask
        return ifftn_safe(fftn_safe(u)*m), ifftn_safe(fftn_safe(v)*m), ifftn_safe(fftn_safe(w)*m)

    def rhs(self,u,v,w):
        nu,nv,nw = self.nonlinear(u,v,w)
        nu,nv,nw = self.dealias(nu,nv,nw)
        uh,vh,wh = fftn_safe(u),fftn_safe(v),fftn_safe(w)
        return self.project(nu+ifftn_safe(-self.nu*self.k2*uh),
                            nv+ifftn_safe(-self.nu*self.k2*vh),
                            nw+ifftn_safe(-self.nu*self.k2*wh))

    def step_rk2(self,dt):
        u0,v0,w0 = self.u,self.v,self.w
        k1u,k1v,k1w = self.rhs(u0,v0,w0)
        k2u,k2v,k2w = self.rhs(u0+0.5*dt*k1u, v0+0.5*dt*k1v, w0+0.5*dt*k1w)
        self.u,self.v,self.w = u0+dt*k2u, v0+dt*k2v, w0+dt*k2w
        self.u,self.v,self.w = self.project(self.u,self.v,self.w)

    def energy(self): return 0.5*float(torch.mean(self.u**2+self.v**2+self.w**2).item())

    def dissipation(self):
        gs = [self.d(f,k) for f in (self.u,self.v,self.w) for k in (self.kx,self.ky,self.kz)]
        return float(self.nu * torch.mean(sum(g*g for g in gs)).item())

    def vort_slice(self):
        wx = self.d(self.w,self.ky)-self.d(self.v,self.kz)
        wy = self.d(self.u,self.kz)-self.d(self.w,self.kx)
        wz = self.d(self.v,self.kx)-self.d(self.u,self.ky)
        mag = torch.sqrt(wx**2+wy**2+wz**2)
        return mag[self.n//2,:,:].detach().cpu().numpy()

    def run(self,t_final,dt,store_every):
        times,Es,eps,slices = [],[],[],[]
        t,step=0.0,0
        while t < t_final-1e-12:
            if step%store_every==0:
                times.append(t); Es.append(self.energy()); eps.append(self.dissipation()); slices.append(self.vort_slice())
            self.step_rk2(dt); t+=dt; step+=1
        times.append(t); Es.append(self.energy()); eps.append(self.dissipation()); slices.append(self.vort_slice())
        return np.array(times),np.array(Es),np.array(eps),slices

def save_energy_plot(times,Es,eps,path):
    fig,(a1,a2)=plt.subplots(2,1,figsize=(8,7),sharex=True)
    a1.semilogy(times,Es,'b-',lw=2); a1.set_ylabel('E(t)'); a1.set_title('TGV energy decay'); a1.grid(True,alpha=0.3)
    a2.plot(times,eps,'r-',lw=2); a2.set_xlabel('t'); a2.set_ylabel('eps(t)'); a2.grid(True,alpha=0.3)
    fig.tight_layout(); path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path,dpi=150); plt.close(fig); print(f"Збережено: {path}")

def run_slice_anim(slices,times,path,fps):
    vmax=max(s.max() for s in slices); vmax=max(vmax,1e-6)
    fig,ax=plt.subplots(figsize=(7,6))
    im=ax.imshow(slices[0],origin='lower',cmap='inferno',vmin=0,vmax=vmax,aspect='equal')
    plt.colorbar(im,ax=ax,label='|omega|'); title=ax.set_title('TGV slice t=0')
    def upd(f):
        im.set_array(slices[f]); title.set_text(f'TGV slice t={times[f]:.3f}'); return [im,title]
    anim=animation.FuncAnimation(fig,upd,frames=len(slices),interval=1000//fps,blit=True)
    w,ext=get_writer(fps); out=path.with_suffix(ext); anim.save(str(out),writer=w,dpi=120); plt.close(fig)
    print(f"Збережено: {out}")

def export_vtk(solver, vtk_dir):
    try: import pyvista as pv
    except ImportError: print("WARNING: pyvista not installed"); return
    vtk_dir.mkdir(parents=True,exist_ok=True)
    n,L=solver.n,solver.L; x=np.linspace(0,L,n,endpoint=False)
    X,Y,Z=np.meshgrid(x,x,x,indexing='ij'); grid=pv.StructuredGrid(X,Y,Z)
    u,v,w=[t.detach().cpu().numpy() for t in (solver.u,solver.v,solver.w)]
    grid['velocity']=np.stack([u,v,w],-1).reshape(-1,3)
    out=vtk_dir/'tgv_final.vtk'; grid.save(str(out)); print(f"VTK: {out}")

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--n',type=int,default=64)
    p.add_argument('--re',type=float,default=1600.0)
    p.add_argument('--t-final',type=float,default=10.0)
    p.add_argument('--dt',type=float,default=0.01)
    p.add_argument('--fps',type=int,default=12)
    p.add_argument('--vtk',action='store_true')
    p.add_argument('--energy-png',type=Path,default=OUTPUT_DIR/'3d_tgv_energy.png')
    p.add_argument('--video',type=Path,default=OUTPUT_DIR/'3d_tgv_slices.mp4')
    args=p.parse_args()
    L=2*np.pi; nu=1.0/args.re; device=get_device()
    solver=TaylorGreenSolver(args.n,nu,L,device)
    se=max(1,int(args.t_final/args.dt)//(args.fps*25))
    print(f"Re={args.re}, grid {args.n}^3")
    times,Es,eps,slices=solver.run(args.t_final,args.dt,se)
    save_energy_plot(times,Es,eps,args.energy_png)
    run_slice_anim(slices,times,args.video,args.fps)
    if args.vtk: export_vtk(solver, OUTPUT_DIR/'vtk')

if __name__=='__main__': main()
