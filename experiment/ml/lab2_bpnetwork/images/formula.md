$$
\begin{aligned}
E_k &= \frac{1}{2}\sum_{j=1}^l(\hat{y}_j^k-{y}_j^k)^2\\
g_j &= \hat{y}_j^k(1-\hat{y}_j^k)({y}_j^k-\hat{y}_j^k)\\
e_h&=b_h(1-b_h)\sum_{j=1}^lw_{hj}g_j\\
\frac{\partial E_k}{\partial w_{hj}}&=g_jb_h\\
\frac{\partial E_k}{\partial v_{ih}}&=e_hx_i\\
\frac{\partial E_k}{\partial \gamma_{h}}&=-e_h\\
\frac{\partial E_k}{\partial \theta_{j}}&=-g_j\\
\end{aligned}
$$

