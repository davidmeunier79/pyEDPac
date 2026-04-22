import numpy as np
from edpac.visualisation.pixel_visualizer import PixelVisualizer

from edpac.config.constants import NB_VISIO_INPUTS, VISIO_SQRT_NB_NEURONS

from edpac.genetic_algorithm.population import Population
from .input_visualizer import InputVisualizer

class MultiInputVisualizer(InputVisualizer):
    def __init__(self, pop , title = "All EDPac inputs", scale = 1):
        # 5 squares of 20x20. With 5px padding, we need ~130px width.
        # Height 30px to accommodate a 20x20 square with padding.

        #self.input_visualizers = List[InputVisualizer]

        #self._init_visualizers(pop)
        self.nb_panels = len(pop.individuals)

        print(self.nb_panels)

        self.nb_input_patterns = 1
        self.square_size = VISIO_SQRT_NB_NEURONS
        self.padding = 5

        # for each visualizer
        self.panel_height = (VISIO_SQRT_NB_NEURONS + 2*self.padding)
        self.panel_width = (1 * (VISIO_SQRT_NB_NEURONS + self.padding) + self.padding)

        print(self.panel_height, self.panel_width)


        height = self.panel_height * int(self.nb_panels // 2)
        width = self.panel_width * 2

        print(height, width)

        super().__init__(height, width,  title=title, scale=scale)
    #
    # def _init_visualizers(self, population, scale):
    #
    #     for i in len(population.individuals):
    #             self.input_visualizers = InputVisualizer(title = f"EDPac inputs {int(i //2)}, {i % 2} " ,scale=scale)

    def _return_root_coords(self, pacman_index):
        root_x = int(pacman_index % 2)
        root_y = int(pacman_index // 2)
        return root_x, root_y

    def _draw_panel_background(self, pacman_index):

        root_x, root_y = self._return_root_coords(pacman_index)

        #print(f"Background {pacman_index}", root_x*self.panel_width, root_y*self.panel_height)

        self.draw_background(root_x*self.panel_width, root_y*self.panel_height)

    def _display_empty_inputs(self, pacman_index):

        root_x, root_y = self._return_root_coords(pacman_index)

        #print(f"Background {pacman_index}", root_x*self.panel_width, root_y*self.panel_height)

        self.draw_empty_inputs(root_x*self.panel_width, root_y*self.panel_height)

    def _display_panel_inputs(self, sensor_values, pacman_index):

        root_x, root_y = self._return_root_coords(pacman_index)

        #print(f"Input {pacman_index}", root_x*self.panel_width, root_y*self.panel_height)

        self.display_inputs(sensor_values, root_x*self.panel_width, root_y*self.panel_height)

    def _display_color_panel_inputs(self, sensor_values, pacman_index, verbose=0):

        root_x, root_y = self._return_root_coords(pacman_index)

        if verbose>0:
            print(f"Input {pacman_index}", root_x*self.panel_width, root_y*self.panel_height)
            print(f"{sensor_values=}")

        self.set_color_pattern(root_x*self.panel_width, root_y*self.panel_height, sensor_values)

    def display_all_backgrounds(self):

        for i in range(self.nb_panels):
            #print(f"Background inputs for {i=}")
            self._draw_panel_background(pacman_index = i)

        self.refresh_from_background()

    def display_all_inputs(self, all_sensor_values):

        self.refresh_from_background()

        assert len(all_sensor_values) == self.nb_panels, f"Error with {len(all_sensor_values)=} != {self.nb_panels=}"

        for i, sensor_values in enumerate(all_sensor_values):

            if sensor_values is not None:
                ## empty sensor_values
                self._display_empty_inputs(pacman_index = i)
            else:
                self._display_panel_inputs(sensor_values, pacman_index = i)

    def display_all_color_inputs(self, all_sensor_values, verbose=0):

        self.refresh_from_background()

        assert len(all_sensor_values) == self.nb_panels, f"Error with {len(all_sensor_values)=} != {self.nb_panels=}"

        for i, sensor_values in enumerate(all_sensor_values):

            if sensor_values is None:
                if verbose > 0:
                    print("empty sensor_values")

                # empty sensor_values
                self._display_empty_inputs(pacman_index = i)
            else:
                if verbose > 0:
                    print("color_panel_inputs")

                # display_color_panel_inputs
                self._display_color_panel_inputs(sensor_values, pacman_index = i)
