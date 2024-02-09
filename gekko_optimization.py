import numpy as np
from gekko import GEKKO
import matplotlib.pyplot as plt

m = GEKKO()

nt = 501
tm = np.linspace(0,1,nt)
m.time = tm

# Variables
x1 = m.Var(value=0.0)
x2 = m.Var(value=0.1)
#x3 = m.Var(value=26630.0)

p = np.zeros(nt)
#p[-1] = 265.0
final = m.Param(value=p)

# FV (Fixed variable)
tf = m.FV(value=1.0,lb=0.1,ub=100.0)
tf.STATUS = 1

# MV (Manipulated variable)
u = m.MV(lb=0,ub=500)
u.STATUS = 1

# Parameters
mass_rider = 78
mass_bike = 8
total_mass =  mass_rider + mass_bike
g = 9.81
my = 0.004
b0 = 0.091
b1 = 0.0087
Iw = 0.14
r = 0.33
Cd = 0.7
rho = 1.2
A = 0.4
eta = 1
w_prime = 26630
cp = 265
# slope = np.sin(np.linspace(0, 10*np.pi, nt)) 
# # Parameter for slope
# slope_param = m.Param(value=slope)

m.Equation(x1.dt()==x2*tf)
#m.Equation(x2.dt()==(1/x2 * 1/(m + Iw/r**2) * (eta*u - m*g*x2*slope - my*m*g*x2 - b0*x2 - b1*x2**2 - 0.5*Cd*rho*A*x2**3))*tf)
m.Equation(x2.dt()==(1/x2 * 1/(total_mass + Iw/r**2) * (eta*u - my*total_mass*g*x2 - b0*x2 - b1*x2**2 - 0.5*Cd*rho*A*x2**3))*tf) # Without any slope
#m.Equation(x3.dt() == m.if3(u - cp, ((1 - x3 / w_prime) * (cp - u))*tf, (-(u - cp)*tf)))


#m.Equation(x1*final >= 1000)
#m.Equation(x3 >= 0)


m.Minimize(tf)

m.options.IMODE = 6
m.solve()

print('Final Time: ' + str(tf.value[0]))

tm = tm * tf.value[0]
print('After scaling: Final Time: ' + str(tf.value[0]))

print(u.value)

plt.figure(1)
plt.plot(tm,x1.value,'k-',lw=2,label=r'$x_1$')
plt.plot(tm,x2.value,'b-',lw=2,label=r'$x_2$')
#plt.plot(tm,x3.value,'g--',lw=2,label=r'$x_3$')
plt.plot(tm,u.value,'r--',lw=2,label=r'$u$')
plt.legend(loc='best')
plt.xlabel('Time')
plt.ylabel('Value')
plt.show()
