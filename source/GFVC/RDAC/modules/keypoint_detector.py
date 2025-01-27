import torch
import torch.nn as nn
import torch.nn.functional as F
from GFVC.RDAC.modules.util import Hourglass,KP_Output, make_coordinate_grid, AntiAliasInterpolation2d

class KPD(nn.Module):
    """
    Detecting a keypoints. Returns keypoint position and jacobian near each keypoint.
    """
    def __init__(self, block_expansion=64, num_kp=10, num_channels=3, max_features=512,
                 num_blocks=3, temperature=0.1, estimate_jacobian=False, scale_factor=1,
                 pad=3, **kwargs):
        super(KPD, self).__init__()

        self.predictor = Hourglass(block_expansion, in_features=num_channels,
                                   max_features=max_features, num_blocks=num_blocks)

        self.kp = KP_Output(in_channels=self.predictor.out_filters, out_channels=num_kp, kernel_size=(7, 7),
                            padding=pad)
        self.jacobian = estimate_jacobian

        self.temperature = temperature
        self.scale_factor = scale_factor
        if self.scale_factor != 1:
            self.down = AntiAliasInterpolation2d(3, self.scale_factor)

    def region2affine(self, region):
        shape = region.shape
        region = region.unsqueeze(-1)
        grid = make_coordinate_grid(shape[2:], region.type()).unsqueeze_(0).unsqueeze_(0)
        kp_coord = (region * grid).sum(dim=(2, 3))
        region_params = {'value': kp_coord}

        if self.jacobian:
            mean_sub = grid - kp_coord.unsqueeze(-2).unsqueeze(-2)
            covar = torch.matmul(mean_sub.unsqueeze(-1), mean_sub.unsqueeze(-2))
            covar = covar * region.unsqueeze(-1)
            covar = covar.sum(dim=(2, 3))
            region_params['jacobian'] = covar
        return region_params

    def forward(self, x):
        if self.scale_factor != 1:
            x = self.down(x)
            
        feature_map = self.predictor(x)

        prediction = self.kp(feature_map)

        final_shape = prediction.shape
        heatmap = prediction.view(final_shape[0], final_shape[1], -1)
        heatmap = F.softmax(heatmap / self.temperature, dim=2)
        heatmap = heatmap.view(*final_shape)

        out = self.region2affine(heatmap)
        out.update({'heatmap': heatmap})        
        return out

