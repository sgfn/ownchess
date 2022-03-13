class Settings:
    """A class to store all settings for ownchess-gui."""

    def __init__(self):
        """Initialise the settings."""

        # Screen settings
        self.scr_width = 1200
        self.scr_height = 800

        # Visual settings
        self.vis_bg_clr = '#222222'
        self.vis_sq_light_clr = '#F0DABA'
        self.vis_sq_dark_clr = '#B59064'
        self.vis_sq_highlight_clr = '#738355'
