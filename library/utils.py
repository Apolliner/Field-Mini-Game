

def gluing_location(raw_gluing_map, grid, count_block):
    """
        Склеивает чанки и локации в единое поле из "сырых" карт

        grid - количество кластеров в одной стороне квадратной склеиваемой карты
        count_block - количество сущностей на одной стороне квадратного кластера
    """
    value_region_box = grid * count_block
    gluing_map = []
    for empry_line in range(grid * count_block):
        gluing_map.append([])

    count_location = 0
    for number_region_line in range(grid):
        for number_region in range(grid):
            for number_location_line in range(count_block):
                for number_location in range(count_block):
                    gluing_index = (number_region_line + number_location_line) + (
                                count_location // (grid * (count_block ** 2)) * (count_block - 1))  # определяет индекс
                    gluing_map[gluing_index].append(
                        raw_gluing_map[number_region_line][number_region][number_location_line][number_location])
                    count_location += 1
    return gluing_map