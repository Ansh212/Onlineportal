import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const DisableBackButton = () => {
  const navigate = useNavigate();

  useEffect(() => {
    window.history.pushState(null, '', window.location.href);

    const handlePopState = (event) => {
      window.history.pushState(null, '', window.location.href);
      alert('Back navigation is disabled');
    };

    window.addEventListener('popstate', handlePopState);

    return () => {
      window.removeEventListener('popstate', handlePopState);
    };
  }, [navigate]);

  return null;
};

export default DisableBackButton;
