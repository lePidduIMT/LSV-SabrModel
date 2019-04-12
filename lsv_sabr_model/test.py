import pytest
import math
from datetime import datetime
from dataclasses import dataclass
import numpy as np
from scipy.integrate import quad, fixed_quad
from src.numerix import lv_sigma, lv_sigma_vectorized, lamperti_transform_lv_sigma, lv_sigma_integrand_scipy

@dataclass
class TestData:
    beta_low: float
    beta_high: float
    epsilon: float
    epsilon_s: float
    Psi: float
    K_high: float
    lambda_: float
    f_low: float
    f_high: float
    forward_rate: float

    def get_params(self):
        return self.beta_low, self.beta_high, self.epsilon, self.epsilon_s, self.Psi, self.K_high, self.lambda_, self.f_low, self.f_high, self.forward_rate


@pytest.fixture
def load_basic_data():
    bl, bh, e, es = 0.265, 0.0, 0.0032, 0.001
    lmbd = 0.5
    psi = 47.7
    F0 = 0.01833
    fl = -0.03
    fh = F0 + 0.5
    kh = F0 + 0.08
    return TestData(bl, bh, e, es, psi, kh, lmbd, fl, fh, F0)

def test_functions_return_value(load_basic_data):
    f = 0.04
    f0 = load_basic_data.forward_rate
    f_array = np.linspace(f0, f)
    extra_args = load_basic_data.get_params()
    try:
        lv_sigma(f, *extra_args)
        lv_sigma_vectorized(f_array, *extra_args)
        lamperti_transform_lv_sigma(f, f0, *extra_args)
    except:
        raise RuntimeError

def test_integration_returns_close_values(load_basic_data):
    f = 0.04
    f0 = load_basic_data.forward_rate
    extra_args = load_basic_data.get_params()
    my_value = lamperti_transform_lv_sigma(f, f0, *extra_args)
    quad_value = quad(lv_sigma, f0, f, args=extra_args)[0]
    assert math.isclose(my_value, quad_value)


def time_compute_local_volatility_lamperti_transform():
    bl, bh, e, es = 0.265, 0.0, 0.0032, 0.001
    lmbd = 0.5
    psi = 47.7
    F0 = 0.01833
    fl = -0.03
    fh = F0 + 0.5
    kh = F0 + 0.08
    test_data = TestData(bl, bh, e, es, psi, kh, lmbd, fl, fh, F0)

    extra_args = test_data.get_params()
    F0 = test_data.forward_rate

    K_array = np.linspace(-0.01, 0.08)
    local_vols_scipy = np.zeros(K_array.size)
    local_vols_numba = np.zeros(K_array.size)
    now = datetime.now()
    for ix, k in enumerate(K_array):
        local_vols_scipy[ix] = quad(lv_sigma_integrand_scipy, a=F0, b=k, args=extra_args)[0]
        local_vols_numba[ix] = lamperti_transform_lv_sigma(k, F0, *extra_args)
    print(local_vols_scipy)
    print(local_vols_numba)
    print(datetime.now() - now)
    


if __name__ == '__main__':
    time_compute_local_volatility_lamperti_transform()
