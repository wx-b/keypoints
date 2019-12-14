import torch
import torch.nn.functional as F


def marginal_softmax(heatmap, dim):
    marginal = torch.mean(heatmap, dim=dim)
    sm = F.softmax(marginal, dim=2)
    return sm


def prob_to_keypoints(prob, length):
    ruler = torch.linspace(0, 1, length).type_as(prob).expand(1, 1, -1).to(prob.device)
    return torch.sum(prob * ruler, dim=2, keepdim=True).squeeze(2)


def spacial_softmax(heatmap, probs=False):
    height, width = heatmap.size(2), heatmap.size(3)
    hp, wp = marginal_softmax(heatmap, dim=3), marginal_softmax(heatmap, dim=2)
    hk, wk = prob_to_keypoints(hp, height), prob_to_keypoints(wp, width)
    if probs:
        return torch.stack((hk, wk), dim=2), (hp, wp)
    else:
        return torch.stack((hk, wk), dim=2)


def squared_diff(h, height):
    hs = torch.linspace(0, 1, height, device=h.device).type_as(h).expand(h.shape[0], h.shape[1], height)
    hm = h.expand(height, -1, -1).permute(1, 2, 0)
    hm = ((hs - hm) ** 2)
    return hm


def gaussian_like_function(kp, height, width, sigma=0.1, eps=1e-6):
    hm = squared_diff(kp[:, :, 0], height)
    wm = squared_diff(kp[:, :, 1], width)
    hm = hm.expand(width, -1, -1, -1).permute(1, 2, 3, 0)
    wm = wm.expand(height, -1, -1, -1).permute(1, 2, 0, 3)
    gm = - (hm + wm + eps).sqrt_() / (2 * sigma ** 2)
    gm = torch.exp(gm)
    return gm
