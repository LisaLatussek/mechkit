#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''Run tests:
    python3 -m pytest
'''
import os
import sys
import numpy as np
import pytest

sys.path.append(os.path.join('..'))
import mechkit
from mechkit import tensors as t
from mechkit import utils

##################################
# Helpers


def assertException(
                func,
                message,
                args=[],
                kwargs={},
                exception=utils.Ex,
                ):
    with pytest.raises(exception) as excinfo:
        func(*args, **kwargs)
    assert str(excinfo.value).startswith(message)
    return None


##################################
# Test


def test_compare_P1_P2_mandel6_tensor():

    con = mechkit.notation.Converter()

    # Prepare
    P1_mandel6 = 1./3. * np.array(
                [
                    [1.0,   1.0,    1.0,    0.0,    0.0,    0.0],
                    [1.0,   1.0,    1.0,    0.0,    0.0,    0.0],
                    [1.0,   1.0,    1.0,    0.0,    0.0,    0.0],
                    [0.0,   0.0,    0.0,    0.0,    0.0,    0.0],
                    [0.0,   0.0,    0.0,    0.0,    0.0,    0.0],
                    [0.0,   0.0,    0.0,    0.0,    0.0,    0.0],
                ],
                dtype='float64',
                )

    I4s_mandel6 = np.eye(6, dtype='float64')

    P2_mandel6 = I4s_mandel6 - P1_mandel6

    # t4_to_mandel
    assert np.allclose(P1_mandel6,  con.to_mandel(t.P1))
    assert np.allclose(P2_mandel6,  con.to_mandel(t.P2))
    assert np.allclose(I4s_mandel6, con.to_mandel(t.I4s))

    # mandel2_to_tensor
    assert np.allclose(t.P1,   con.to_tensor(P1_mandel6))
    assert np.allclose(t.P2,   con.to_tensor(P2_mandel6))
    assert np.allclose(t.I4s,  con.to_tensor(I4s_mandel6))


def test_level2_mandel6_tensor():

    con = mechkit.notation.Converter()

    mandel = np.array(
            [
                1.0,
                2.0,
                3.0,
                np.sqrt(2)*4.0,
                np.sqrt(2)*5.0,
                np.sqrt(2)*6.0,
            ],
            dtype='float64')

    tensor = np.array([
                    [1., 6., 5.],
                    [6., 2., 4.],
                    [5., 4., 3.],
                    ])

    assert np.allclose(con.to_mandel(tensor), mandel)
    assert np.allclose(con.to_tensor(mandel), tensor)


def test_level4_mandel6_tensor():

    con = mechkit.notation.Converter()
    factor = np.sqrt(2.)
    mandel = np.array(
        [
            [1.,         1.,         1.,         factor, factor, factor],
            [1.,         1.,         1.,         factor, factor, factor],
            [1.,         1.,         1.,         factor, factor, factor],
            [factor, factor, factor, 2.,         2.,         2.],
            [factor, factor, factor, 2.,         2.,         2.],
            [factor, factor, factor, 2.,         2.,         2.],
        ],
        dtype='float64',
        )

    tensor = np.ones((3, 3, 3, 3))

    assert np.allclose(con.to_mandel(tensor), mandel)
    assert np.allclose(con.to_tensor(mandel), tensor)


def test_pass_throught():

    con = mechkit.notation.Converter(skew=True)

    m2 = np.random.rand(9, )
    m4 = np.random.rand(9, 9,)
    t2 = np.random.rand(3, 3,)
    t4 = np.random.rand(3, 3, 3, 3,)

    assert np.allclose(con.to_mandel(m2),   m2)
    assert np.allclose(con.to_mandel(m4),   m4)
    assert np.allclose(con.to_tensor(t2),   t2)
    assert np.allclose(con.to_tensor(t4),   t4)


def test_mandel6_to_tensor_to_mandel6():

    con = mechkit.notation.Converter()
    matrix = np.random.rand(6, 6)
    assert np.allclose(con.to_mandel(con.to_tensor(matrix)), matrix)


def test_tensor_to_mandel6_to_tensor():

    con = mechkit.notation.Converter()

    tensor = np.random.rand(3, 3, 3, 3)
    tensor_sym_minor = 0.25*(
                tensor.transpose([0, 1, 2, 3])
                + tensor.transpose([1, 0, 2, 3])
                + tensor.transpose([0, 1, 3, 2])
                + tensor.transpose([1, 0, 3, 2]))
    matrix = con.to_mandel(tensor_sym_minor)

    assert np.allclose(con.to_tensor(matrix), tensor_sym_minor)


def test_mandel9_to_tensor_to_mandel9():

    con = mechkit.notation.Converter(skew=True)
    matrix = np.random.rand(9, 9)
    assert np.allclose(con.to_mandel(con.to_tensor(matrix)), matrix)


def test_tensor_to_mandel9_to_tensor():

    con = mechkit.notation.Converter(skew=True)
    tensor = np.random.rand(3, 3, 3, 3)
    assert np.allclose(con.to_tensor(con.to_mandel(tensor)), tensor)


def test_ones_tensors_to_mandel6_to_voigt_to_mandel6():
    '''Define ones tensors and transform to Mandel.

    Ones tensors are useful to visualize the conversions.
    Ones tensors are not useful to check correct implementation!
    Convert this mandel representation to Voigt and back
    to mandel and compare with initial mandel representation'''

    converter = mechkit.notation.VoigtConverter()

    ones2_mandel = converter.to_mandel(tensor=np.ones((3, 3),))
    ones4_mandel = converter.to_mandel(tensor=np.ones((3, 3, 3, 3),))

    voigt_types = {
        'stress': ones2_mandel,
        'strain': ones2_mandel,
        'stiffness': ones4_mandel,
        'compliance': ones4_mandel,
        }

    print('#####################')
    print('Input in Mandel')
    for voigt_type, inp in voigt_types.items():
        print(voigt_type)
        print(inp)

    print('#####################')
    print('In Voigt')
    voigts = {}

    for voigt_type, input_mandel in voigt_types.items():
        out = converter.mandel_to_voigt(
                        mandel=input_mandel,
                        voigt_type=voigt_type,
                        )
        print(voigt_type)
        print(out)

        voigts[voigt_type] = out

    print('#####################')
    print('Back in Mandel')
    mandels = {}

    for voigt_type, voigt in voigts.items():
        out = converter.voigt_to_mandel(
                        voigt=voigt,
                        voigt_type=voigt_type,
                        )
        print(voigt_type)
        print(out)

        mandels[voigt_type] = out

    for voigt_type, mandel in mandels.items():
        assert np.allclose(
                        mandel,
                        voigt_types[voigt_type],
                        )


##################################
# Test eigenvalues

def isotropic_stiffness_mandel6(EW1, EW2):
    con = mechkit.notation.Converter()
    tensors = mechkit.tensors
    P1 = con.to_mandel(tensors.P1)
    P2 = con.to_mandel(tensors.P2)
    return P1 * EW1 + P2 * EW2


def compare_matrix_eigenvalues_with_list_of_numbers(
                        matrix,
                        list_of_numbers,
                        decimals=7,
                        ):
    boolean = set(np.linalg.eig(matrix)[0].round(decimals=decimals)) \
              == set(
                    np.array(
                        list_of_numbers,
                        ).round(decimals=decimals)
                    )
    return boolean


def test_eigenvalues_of_isotropic_stiffness_mandel6():
    EW1 = 1500
    EW2 = 700

    C = isotropic_stiffness_mandel6(EW1, EW2)

    assert compare_matrix_eigenvalues_with_list_of_numbers(
                        matrix=C,
                        list_of_numbers=[EW1, EW2],
                        )


def test_eigenvalues_of_inverse_of_isotropic_stiffness_mandel6():
    EW1 = 1500
    EW2 = 700

    C = isotropic_stiffness_mandel6(EW1, EW2)

    C_inv = np.linalg.inv(C)

    assert compare_matrix_eigenvalues_with_list_of_numbers(
                    matrix=C_inv,
                    list_of_numbers=[1./EW1, 1./EW2],

                    )


if __name__ == '__main__':
    test_ones_tensors_to_mandel6_to_voigt_to_mandel6()
    test_level4_mandel6_tensor()
    test_tensor_to_mandel6_to_tensor()
