def calc_radius_of_gyration_and_cm_from_A(A_list):
    """
    A_list: lista de [x, y, z] (matriz A).
    Devuelve: (r, CM) donde r es el radio de giro (según tu fórmula en MATLAB)
              y CM es [CMx, CMy, CMz].
    """
    A = np.asarray(A_list, dtype=float)
    nTotal = A.shape[0]
    if nTotal == 0:
        return 0.0, [0.0, 0.0, 0.0]

    # Centro de masa
    CM = A.mean(axis=0)

    # TU FORMULA en MATLAB hace:
    # Suma = (1/n^2) * sum_{i,j} ||ri - rj||^2
    # r = sqrt(Suma)
    # Podemos calcularla de forma equivalente y O(n) en memoria:
    # mean_pairwise_sq = 2 * mean( ||ri - CM||^2 )
    dif = A - CM
    mean_sq_to_CM = np.mean(np.sum(dif * dif, axis=1))
    mean_pairwise_sq = 2.0 * mean_sq_to_CM
    r = float(np.sqrt(mean_pairwise_sq))
    return r, [float(CM[0]), float(CM[1]), float(CM[2])]
